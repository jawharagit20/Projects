#!/bin/bash

echo "Creating server keystore..."
keytool -genkeypair -alias server -keyalg RSA -keysize 2048 -keystore server.jks -storepass serverpass -keypass serverpass -dname "CN=localhost, OU=IT, O=Company, L=City, S=State, C=US" -validity 365

echo "Exporting server certificate..."
keytool -exportcert -alias server -keystore server.jks -storepass serverpass -file server.crt

echo "Creating client truststore..."
keytool -genkeypair -alias client -keyalg RSA -keysize 2048 -keystore client.jks -storepass clientpass -keypass clientpass -dname "CN=client, OU=IT, O=Company, L=City, S=State, C=US" -validity 365

echo "Importing server certificate into client truststore..."
keytool -importcert -alias server -keystore client.jks -storepass clientpass -file server.crt -noprompt

echo "Done! Created server.jks and client.jks"
echo "Make sure to place these files in the same directory as your Java files."