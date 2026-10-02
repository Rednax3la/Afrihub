# Vernaculearn Android package

1. Install Node.js, then Bubblewrap: `npm install -g @bubblewrap/cli`.
2. From this directory run `bubblewrap init --manifest https://vernaculearn.africa/manifest.json`. Allow Bubblewrap to install its Android SDK/JDK dependencies when prompted.
3. Merge the generated values into `twa-manifest.json`, preserving the package ID `africa.vernaculearn.app`, host, colors, start URL, and shortcuts. Keep generated SDK, version, signing-key, and icon settings. The checked-in file is a starting configuration, not a complete generated Android project. Use square 512px launcher and maskable icons with appropriate safe areas before release.
4. Run `bubblewrap build` to generate the APK and Android App Bundle. Keep the generated keystore and its password securely backed up, outside source control.
5. Bubblewrap normally signs during the build. If you need to sign an unsigned AAB manually with the generated keystore, run `jarsigner -keystore <keystore-path> <unsigned-bundle.aab> <key-alias>`. Verify with `jarsigner -verify -verbose -certs <bundle.aab>`. For an unsigned APK use Android SDK `zipalign` then `apksigner`; jarsigner alone does not provide modern APK signing schemes. Do not re-sign an already signed artifact.
6. Upload the signed AAB to Google Play Console on an **internal test track** first. Configure Play App Signing and test installation, sign-in, navigation, offline behavior, and payments on a physical device.

## Associate the website with the app

Publish `https://vernaculearn.africa/.well-known/assetlinks.json` with relation `delegate_permission/common.handle_all_urls`, namespace `android_app`, package name `africa.vernaculearn.app`, and the SHA-256 certificate fingerprint from **Play App Signing** (the installed app certificate). Include your local signing certificate separately if testing a locally signed APK. Without this association the app opens a browser toolbar instead of a verified TWA.

The site must serve the manifest, service worker, icons, and SPA routes over HTTPS. Test the root and deep links before building. Supply Play listing assets, privacy policy, content rating, and data safety declarations. Confirm the applicable Play billing requirements for digital subscriptions and your intended markets before release; a TWA does not itself exempt subscriptions from Play billing rules.

References: [Bubblewrap CLI](https://github.com/GoogleChromeLabs/bubblewrap/tree/main/packages/cli), [Google Play payments policy](https://support.google.com/googleplay/android-developer/answer/9858738).
