#!/usr/bin/env bash

echo "Create keychain"
security create-keychain -p $CERTIFICATE_PASSWORD electron-app-build.keychain
security default-keychain -s electron-app-build.keychain

KEYCHAIN=~/Library/Keychains/electron-app-build.keychain

echo "Adding distribution key"
security import resource/cert.p12 -k $KEYCHAIN -P $CERTIFICATE_PASSWORD -T /usr/bin/codesign

echo "Unlock keychain"
security unlock-keychain -p $CERTIFICATE_PASSWORD electron-app-build.keychain

echo "Increase keychain unlock timeout"
security set-keychain-settings -lut 3600 electron-app-build.keychain

echo "Add keychain to keychain-list"
security list-keychains -s electron-app-build.keychain
