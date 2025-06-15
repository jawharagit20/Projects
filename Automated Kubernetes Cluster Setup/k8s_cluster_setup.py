#!/usr/bin/env python3
from __future__ import annotations
import argparse, atexit, logging, os, shlex, signal, subprocess, sys, time, yaml
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Tuple, Optional
import paramiko

# ────────── logging ──────────
LOG_FMT = "%(asctime)s  %(levelname)-8s  %(message)s"
root = logging.getLogger(); root.setLevel(logging.INFO)
for h in (logging.StreamHandler(sys.stdout),
          logging.FileHandler("k8s_setup.log", encoding="utf-8")):
    h.setFormatter(logging.Formatter(LOG_FMT)); root.addHandler(h)
log = logging.getLogger(__name__)

# ────────── chatty step helper ──────────
class Phase:
    """Context manager that prints 'Doing X …' then '✓ X done'."""
    def __init__(self, host: str, start: str, done: str): self.h, self.start, self.done = host, start, done
    def __enter__(self):  log.info("%s … %s", self.start, self.h)
    def __exit__(self, exc_type, *_):  # only on success
        if exc_type is None: log.info("✓ %s %s", self.done, self.h)

# ────────── inventory parser ──────────
def parse_inventory(path: str) -> Tuple[dict, dict]:
    if not os.path.isfile(path): raise FileNotFoundError(path)
    cluster, hosts, defaults = {"master": None, "workers": []}, {}, {}
    lines, section = Path(path).read_text().splitlines(), None

    for ln in lines:       # collect [all:vars]
        t = ln.strip()
        if t.startswith("[") and t.endswith("]"): section = t[1:-1].lower(); continue
        if section == "all:vars" and "=" in t and not t.startswith("#"):
            k, v = [s.strip() for s in t.split("=", 1)]; defaults[k] = v.strip("'\"")

    def apply(d): [d.setdefault(k, v) for k, v in defaults.items()]
    section = None
    for ln in lines:       # hosts
        t = ln.strip()
        if not t or t.startswith("#"): continue
        if t.startswith("[") and t.endswith("]"):
            section = t[1:-1].lower(); continue
        if section not in {"master", "workers"}: continue
        parts, alias = t.split(), t.split()[0]; vars_d = {}
        for kv in parts[1:]:
            if "=" in kv: k, v = kv.split("=", 1); vars_d[k] = v.strip("'\"")
        apply(vars_d)
        if "ansible_password" in vars_d and "ansible_ssh_pass" not in vars_d:
            vars_d["ansible_ssh_pass"] = vars_d["ansible_password"]
        if "ansible_pass" in vars_d and "ansible_ssh_pass" not in vars_d:
            vars_d["ansible_ssh_pass"] = vars_d["ansible_pass"]

        ip, user = vars_d.get("ansible_host", alias), vars_d.get("ansible_user", "root")
        hosts[ip] = {"user": user, "password": vars_d.get("ansible_ssh_pass"),
                     "pkey": vars_d.get("ansible_ssh_private_key_file"),
                     "port": int(vars_d.get("ansible_port", 22))}
        entry = {"alias": alias, "host": ip, "user": user}
        if section == "master":
            if cluster["master"]: raise ValueError("multiple hosts in [master]")
            cluster["master"] = entry
        else: cluster["workers"].append(entry)
    if not cluster["master"]: raise ValueError("no [master] host in inventory")
    return cluster, hosts

# ────────── SSH runner (connection pool) ──────────
def _esc(pw: str) -> str: return "'" + pw.replace("'", r"'\''") + "'"
class Runner:
    def __init__(self, hosts):
        self.hosts, self.pool = hosts, {}
        atexit.register(self.close_all)
        signal.signal(signal.SIGINT, lambda *_: (self.close_all(), sys.exit(1)))
    def _client(self, h):
        if h in self.pool: return self.pool[h]
        c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        kw = dict(hostname=h, port=self.hosts[h]["port"], username=self.hosts[h]["user"],
                  timeout=20, look_for_keys=False, allow_agent=False)
        if self.hosts[h].get("password"): kw["password"] = self.hosts[h]["password"]
        else: kw["key_filename"] = self.hosts[h]["pkey"]
        c.connect(**kw); self.pool[h] = c; log.debug("[%s] SSH opened", h); return c
    def close_all(self):
        for h, c in self.pool.items():
            try: c.close(); log.debug("[%s] SSH closed", h)
            except: pass
        self.pool.clear()
    def _sudo(self, cmd, h):
        if self.hosts[h]["user"] == "root": return cmd
        pw = self.hosts[h]["password"];  # guaranteed present by inventory parser
        return f"echo {_esc(pw)} | sudo -S -p '' bash -c {shlex.quote(cmd)}"
    def __call__(self, cmd, *, host="localhost", timeout=600, ignore=False):
        try:
            if host == "localhost": return self._local(cmd, timeout)
            return self._remote(cmd, host, timeout)
        except Exception as e:
            if ignore: log.warning("[%s] ignored: %s", host, e); return 1, "", str(e)
            raise
    @staticmethod
    def _local(cmd, t):
        p = subprocess.Popen(cmd, shell=True, text=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        returncode, out, err = p.wait(t), p.stdout.read(), p.stderr.read(); return returncode, out, err
    def _remote(self, cmd, h, t):
        full = self._sudo(cmd, h); log.debug("[%s] $ %s", h, full)
        ssh = self._client(h); stdin, stdout, stderr = ssh.exec_command(full, timeout=t)
        rc = stdout.channel.recv_exit_status()
        out, err = stdout.read().decode(), stderr.read().decode()
        if rc: log.debug("[%s] ERR: %s", h, err.strip())
        return rc, out, err

# ────────── K8s bootstrapper ──────────
class K8s:
    def __init__(self, inv):
        self.cluster, self.hosts = parse_inventory(inv)
        self.run = Runner(self.hosts)
        self.join_cmd: Optional[str] = None

    # ----- helper wrappers -----
    def _cleanup(self, h):
        with Phase(h, "Cleaning", "Cleaned"):
            cmds = [
                "systemctl stop kubelet containerd docker || true",
                "kubeadm reset -f || true",
                "apt-get purge -y kubeadm kubelet kubectl kubernetes-cni kube* || true",
                "apt-get autoremove -y || true",
                "rm -rf /etc/kubernetes /var/lib/etcd /var/lib/kubelet /var/lib/cni /etc/cni /opt/cni || true",
                "iptables -F && iptables -t nat -F && iptables -t mangle -F || true",
                "ip link delete cni0 2>/dev/null || true",
                "fuser -k 6443/tcp 10257/tcp 10259/tcp 2>/dev/null || true",
                "ctr --namespace k8s.io c ls -q | xargs -r ctr --namespace k8s.io c rm || true",
            ]
            for c in cmds: self.run(c, host=h, ignore=True, timeout=300)

    def _apt_update(self, h):
        self.run("DEBIAN_FRONTEND=noninteractive apt-get update -y", host=h)

    def _deps(self, h):
        with Phase(h, "Installing dependencies", "Dependencies installed"):
            pk = ("apt-transport-https ca-certificates curl gnupg lsb-release "
                  "containerd docker.io bridge-utils")
            self._apt_update(h)
            self.run(f"DEBIAN_FRONTEND=noninteractive apt-get install -y {pk}", host=h)

    def _sys(self, h):
        with Phase(h, "Configuring system", "System configured"):
            self.run("swapoff -a", host=h, ignore=True)
            self.run("sed -ri 's/(.* swap .*)/#\\1/' /etc/fstab", host=h, ignore=True)
            mods = "overlay\nbr_netfilter\nbridge\n"
            self.run(f"echo '{mods}' > /etc/modules-load.d/k8s.conf", host=h)
            for m in ["overlay", "br_netfilter", "bridge"]:
                self.run(f"modprobe {m}", host=h, ignore=True)
            sysctl_cfg = ("net.bridge.bridge-nf-call-iptables=1\n"
                          "net.bridge.bridge-nf-call-ip6tables=1\n"
                          "net.ipv4.ip_forward=1\n")
            self.run(f"echo '{sysctl_cfg}' > /etc/sysctl.d/k8s.conf", host=h)
            self.run("sysctl --system", host=h)

    def _containerd(self, h):
        with Phase(h, "Setting up containerd", "Containerd ready"):
            self.run("mkdir -p /etc/containerd", host=h)
            self.run("containerd config default > /etc/containerd/config.toml", host=h)
            self.run("sed -ri 's/SystemdCgroup = false/SystemdCgroup = true/' "
                     "/etc/containerd/config.toml", host=h)
            self.run("systemctl restart containerd && systemctl enable containerd", host=h)

    def _k8s_pkgs(self, h):
        with Phase(h, "Installing Kubernetes packages", "Packages installed"):
            repo = "https://pkgs.k8s.io/core:/stable:/v1.29/deb/"
            self.run("mkdir -p /etc/apt/keyrings", host=h)
            self.run(f"curl -fsSL {repo}Release.key | gpg --dearmor "
                     "-o /etc/apt/keyrings/kubernetes-apt-keyring.gpg", host=h)
            self.run("echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] "
                     f"{repo} /' > /etc/apt/sources.list.d/kubernetes.list", host=h)
            self._apt_update(h)
            self.run("DEBIAN_FRONTEND=noninteractive apt-get install -y kubelet kubeadm kubectl", host=h)
            self.run("apt-mark hold kubelet kubeadm kubectl", host=h)

    def _init_master(self, h):
        with Phase(h, "Initializing control-plane", "Control-plane initialized"):
            rc, _, err = self.run("kubeadm init --pod-network-cidr=10.244.0.0/16 "
                                  "--ignore-preflight-errors=all", host=h, timeout=900)
            if rc: raise RuntimeError(f"master init failed: {err}")

        # kubeconfig
        ssh_user = self.hosts[h]["user"]
        self.run("mkdir -p /root/.kube && cp /etc/kubernetes/admin.conf /root/.kube/config", host=h)
        if ssh_user != "root":
            self.run(f"mkdir -p /home/{ssh_user}/.kube && "
                     f"cp /etc/kubernetes/admin.conf /home/{ssh_user}/.kube/config && "
                     f"chown {ssh_user}:{ssh_user} /home/{ssh_user}/.kube/config", host=h)

        # CNI
        self.run("kubectl apply -f "
                 "https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml",
                 host=h, timeout=180)

        # join command
        rc, out, _ = self.run("kubeadm token create --print-join-command", host=h)
        if rc or not out.strip(): raise RuntimeError("cannot obtain join command")
        self.join_cmd = out.strip()
        Path("join_command.yml").write_text(yaml.safe_dump({"join": self.join_cmd}))
        log.info("join command saved to join_command.yml")

    def _join_worker(self, h):
        if not self.join_cmd: raise RuntimeError("join command not set")
        with Phase(h, "Joining node", "Node joined"):
            rc, _, _ = self.run(self.join_cmd, host=h, timeout=600, ignore=True)
            if rc:
                ign = ("--ignore-preflight-errors="
                       "FileContent--proc-sys-net-bridge-bridge-nf-call-iptables,"
                       "FileContent--proc-sys-net-bridge-bridge-nf-call-ip6tables")
                rc, _, err = self.run(f"{self.join_cmd} {ign}", host=h, timeout=600)
                if rc: raise RuntimeError(f"worker {h} failed: {err}")

    # ----- orchestration -----
    def _prep(self, h):
        self._cleanup(h); self._deps(h); self._sys(h); self._containerd(h); self._k8s_pkgs(h)
    def _worker_pipeline(self, h): self._prep(h); self._join_worker(h)

    def _wait(self, master, timeout=420):
        with Phase(master, "Waiting for cluster readiness", "Cluster Ready"):
            start = time.time()
            while time.time() - start < timeout:
                rc, out, _ = self.run("kubectl get nodes --no-headers", host=master, ignore=True)
                if rc == 0 and out.strip():
                    if all((" Ready " in l or l.split()[1] == "Ready") for l in out.strip().splitlines()): return
                time.sleep(10)
            raise RuntimeError("nodes did not become Ready in time")

    def bootstrap(self, master_only=False, workers_only=False):
        log.info("=== BOOTSTRAP START ===")
        m = self.cluster["master"]["host"]
        if not workers_only:
            self._prep(m); self._init_master(m)
        if not master_only and self.cluster["workers"]:
            with ThreadPoolExecutor(max_workers=min(5, len(self.cluster["workers"]))) as p:
                for f in as_completed([p.submit(self._worker_pipeline, w["host"])
                                       for w in self.cluster["workers"]]): f.result()
        self._wait(m); log.info("=== BOOTSTRAP DONE ===")

    def reset(self):
        log.info("=== RESET START ===")
        self._cleanup(self.cluster["master"]["host"])
        for w in self.cluster["workers"]: self._cleanup(w["host"])
        log.info("=== RESET COMPLETE ===")

# ────────── CLI ──────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--inventory", default="inventory.ini")
    ap.add_argument("--reset", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--master-only", action="store_true")
    g.add_argument("--workers-only", action="store_true")
    a = ap.parse_args()
    if a.verbose: root.setLevel(logging.DEBUG)
    k = K8s(a.inventory)
    (k.reset() if a.reset else k.bootstrap(master_only=a.master_only,
                                           workers_only=a.workers_only))

if __name__ == "__main__":
    main()
