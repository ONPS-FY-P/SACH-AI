# Exact frontend edits

The archive is ready to use. Paths below are relative to the `naaya-mobile-source` project root. To update an existing project, replace each listed file with the delivered file; remove the explicitly deleted files. Keep your raw data and assets.

## Replace these existing frontend files

| File | Action |
|---|---|
| `mobile/.env.example` | Replace with delivered version |
| `mobile/app.config.ts` | Replace with delivered version |
| `mobile/eas.json` | Replace with delivered version |
| `mobile/package-lock.json` | Replace with delivered version |
| `mobile/package.json` | Replace with delivered version |
| `mobile/src/app/(tabs)/index.tsx` | Replace with delivered version |
| `mobile/src/app/account.tsx` | Replace with delivered version |
| `mobile/src/components/Header.tsx` | Replace with delivered version |
| `mobile/src/context/AppContext.tsx` | Replace with delivered version |
| `mobile/src/data/uiText.ts` | Replace with delivered version |
| `mobile/src/hooks/useVoiceInput.ts` | Replace with delivered version |
| `mobile/src/services/api.ts` | Replace with delivered version |
| `mobile/src/types.ts` | Replace with delivered version |

## Add these frontend files

- `mobile/.env`
- `mobile/app.json`
- `mobile/src/services/speech.ts`

## Delete these old files

- `backend/app/auth.py`
- `backend/data/corpus-manifest.json`
- `backend/data/legal-corpus.json`
- `backend/prepare_data.py`
- `mobile/src/services/google.ts`

Replace all delivered `backend/app` modules, requirements, Docker files and tests; add `backend/ingest.py`, `backend/scripts/smoke_test.py`, `backend/.env`, root `compose.yaml` and `deploy/Caddyfile`. The old keyword-only corpus and `prepare_data.py` are removed. The raw JSON files are unchanged.

## Why screen files have small edits

Removing Google authentication necessarily changes authentication controls: the account screen keeps its existing card/buttons/styles, but the Google action becomes a clear-chat action with an appropriate icon. The chat screen loses its obsolete login error action and auth gating. Header account icon remains the previous signed-out icon. No theme, styles, spacing or main screen layouts were redesigned.

## Dependency commands

The updated `package.json` and `package-lock.json` are supplied together. Run `npm ci` from `mobile`. The Google sign-in dependency is removed. SDK-compatible `expo-font` and `expo-asset` are direct dependencies because Expo Doctor found the existing icon/audio modules need them in native builds. No other UI framework is introduced.

## Exact before/after diffs

In each unified diff below, `-` is the original line and `+` is the replacement. Unchanged context locates the edit. For a full replacement rather than patching individual lines, use `COMPLETE_CODE.md`. The npm lockfile is supplied whole in the ZIP rather than duplicating its generated dependency graph here.

### mobile/.env.example

```diff
--- before/mobile/.env.example
+++ after/mobile/.env.example
@@ -1,8 +1 @@
-# Public values are embedded in the mobile app. NEVER put a Groq key here.
-# Replace this IP with the IPv4 address shown by ipconfig on your laptop.
 EXPO_PUBLIC_API_URL=http://192.168.1.5:8000
-EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID=
-# Optional iOS configuration:
-EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID=
-GOOGLE_IOS_URL_SCHEME=
-APP_VARIANT=development
```

### mobile/app.config.ts

```diff
--- before/mobile/app.config.ts
+++ after/mobile/app.config.ts
@@ -1,27 +1,14 @@
 import type { ExpoConfig, ConfigContext } from 'expo/config';
-
-export default ({ config }: ConfigContext): ExpoConfig => ({
-  ...config,
-  name: 'Naaya AI', slug: 'naaya-mobile', version: '1.0.0',
-  platforms: ['android', 'ios'],
-  scheme: 'naaya', orientation: 'portrait', userInterfaceStyle: 'light',
-  icon: './assets/icon.png',
-  ios: {
-    bundleIdentifier: 'com.vedant.naaya', supportsTablet: true,
-    infoPlist: {
-      NSMicrophoneUsageDescription: 'Record a question to transcribe with the online assistant.',
-      ...(process.env.APP_VARIANT === 'development' ? { NSAppTransportSecurity: { NSAllowsLocalNetworking: true } } : {}),
-    },
-  },
-  android: { package: 'com.vedant.naaya', softwareKeyboardLayoutMode: 'resize' },
-  plugins: [
-    'expo-router', 'expo-secure-store',
-    ['expo-audio', { microphonePermission: 'Record a question for Naaya.', enableBackgroundPlayback: false, enableBackgroundRecording: false }],
-    ['expo-build-properties', { android: { usesCleartextTraffic: process.env.APP_VARIANT === 'development' } }],
-    // Android autolinks Google Sign-In. The config plugin registers the iOS callback scheme.
-    ...(process.env.GOOGLE_IOS_URL_SCHEME ? [['@react-native-google-signin/google-signin', { iosUrlScheme: process.env.GOOGLE_IOS_URL_SCHEME }] as [string, Record<string, string>]] : []),
-  ],
-  experiments: { typedRoutes: true },
-  // For EAS builds, add extra: { eas: { projectId: YOUR_PROJECT_UUID } } here.
-  // The setup guide explains how to get this ID with eas init.
-});
+// app.json holds the static configuration, including the ID written by eas init.
+export default ({ config }: ConfigContext): ExpoConfig => {
+  const local = ['development', 'lan'].includes(process.env.APP_VARIANT ?? 'development');
+  return {
+    ...config,
+    name: config.name ?? 'Naaya AI', slug: config.slug ?? 'naaya-mobile',
+    ios: { ...config.ios, infoPlist: {
+      ...config.ios?.infoPlist,
+      ...(local ? { NSAppTransportSecurity: { NSAllowsLocalNetworking: true } } : {}),
+    } },
+    plugins: [...(config.plugins ?? []), ['expo-build-properties', { android: { usesCleartextTraffic: local } }]],
+  };
+};
```

### mobile/eas.json

```diff
--- before/mobile/eas.json
+++ after/mobile/eas.json
@@ -2,6 +2,7 @@
   "cli": { "version": ">= 16.0.0", "appVersionSource": "local" },
   "build": {
     "development": { "developmentClient": true, "distribution": "internal", "environment": "development", "env": { "APP_VARIANT": "development" }, "android": { "buildType": "apk" } },
+    "lan": { "distribution": "internal", "environment": "development", "env": { "APP_VARIANT": "lan" }, "android": { "buildType": "apk" } },
     "preview": { "distribution": "internal", "environment": "preview", "env": { "APP_VARIANT": "preview" }, "android": { "buildType": "apk" } },
     "production": { "environment": "production", "env": { "APP_VARIANT": "production" }, "android": { "buildType": "app-bundle" } }
   }
```

### mobile/package.json

```diff
--- before/mobile/package.json
+++ after/mobile/package.json
@@ -4,15 +4,16 @@
   "main": "expo-router/entry",
   "dependencies": {
     "@expo/vector-icons": "^15.0.2",
-    "@react-native-google-signin/google-signin": "^16.1.5",
     "eslint": "^9.39.5",
     "eslint-config-expo": "~57.0.2",
     "expo": "~57.0.27",
+    "expo-asset": "~57.0.19",
     "expo-audio": "~57.0.5",
     "expo-build-properties": "~57.0.22",
     "expo-constants": "~57.0.21",
     "expo-dev-client": "~57.0.19",
     "expo-file-system": "~57.0.7",
+    "expo-font": "~57.0.4",
     "expo-linking": "~57.0.12",
     "expo-router": "~57.0.25",
     "expo-secure-store": "~57.0.4",
```

### mobile/src/app/(tabs)/index.tsx

```diff
--- before/mobile/src/app/(tabs)/index.tsx
+++ after/mobile/src/app/(tabs)/index.tsx
@@ -1,12 +1,12 @@
 import { useCallback, useRef, useState } from 'react';
 import { ActivityIndicator, KeyboardAvoidingView, Modal, Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
 import { Ionicons } from '@expo/vector-icons';
-import { router, useFocusEffect } from 'expo-router';
-import * as Speech from 'expo-speech';
+import { useFocusEffect } from 'expo-router';
+import * as Speech from '../../services/speech';
 import { SafeAreaView, useSafeAreaInsets } from 'react-native-safe-area-context';
 import { useApp } from '../../context/AppContext';
 import { useVoiceInput } from '../../hooks/useVoiceInput';
-import { api, ApiError } from '../../services/api';
+import { api } from '../../services/api';
 import { Message, Source } from '../../types';
 import { colors, ui } from '../../theme';
 
@@ -16,38 +16,37 @@
   mr: ['ऑनलाइन फसवणुकीत माझे पैसे गेले', 'माझी वस्तू खराब आली आहे', 'अनुच्छेद 21 काय संरक्षण देतो?'],
 };
 export default function ChatScreen() {
-  const { language, t, messages, setMessages, token, authReady } = useApp();
+  const { language, t, messages, setMessages, ready } = useApp();
   const [draft, setDraft] = useState(''); const [busy, setBusy] = useState(false);
-  const [error, setError] = useState(''); const [needsLogin, setNeedsLogin] = useState(false);
+  const [error, setError] = useState('');
   const [sources, setSources] = useState<Source[] | null>(null); const [speaking, setSpeaking] = useState<string | null>(null);
   const scroll = useRef<ScrollView>(null); const sending = useRef(false); const insets = useSafeAreaInsets();
-  const voice = useVoiceInput(language, token, setDraft);
+  const voice = useVoiceInput(language, setDraft);
   const cancelVoice = voice.cancel;
   useFocusEffect(useCallback(() => () => { cancelVoice(); void Speech.stop(); setSpeaking(null); }, [cancelVoice]));
   async function send() {
     const text = draft.trim(); if (!text || sending.current || voice.recording || voice.processing) return;
-    sending.current = true; setBusy(true); setError(''); setNeedsLogin(false); setDraft(''); void Speech.stop(); setSpeaking(null);
-    const outgoing: Message = { id: Date.now().toString(), role: 'user', content: text };
+    sending.current = true; setBusy(true); setError(''); setDraft(''); void Speech.stop(); setSpeaking(null);
+    const outgoing: Message = { id: Date.now().toString(), role: 'user', content: text, language };
     const next = [...messages, outgoing]; setMessages(next);
     try {
-      const result = await api.chat(next, language, token);
-      const incoming: Message = { id: `${Date.now()}-reply`, role: 'assistant', content: result.answer, sources: result.sources };
+      const result = await api.chat(next, language);
+      const incoming: Message = { id: `${Date.now()}-reply`, role: 'assistant', content: result.answer, sources: result.sources, language: result.language };
       setMessages(prev => prev.at(-1)?.id === outgoing.id ? [...prev, incoming] : prev);
     } catch (err) {
       setMessages(prev => prev.filter(m => m.id !== outgoing.id)); setDraft(text);
       setError(err instanceof Error ? err.message : 'Unable to get a response.');
-      setNeedsLogin(err instanceof ApiError && err.status === 401);
     } finally { setBusy(false); sending.current = false; }
   }
   async function read(message: Message) {
     await Speech.stop();
     if (speaking === message.id) { setSpeaking(null); return; }
     setSpeaking(message.id);
-    Speech.speak(message.content.replace(/\[S\d+\]/g, ''), {
-      language: { en: 'en-IN', hi: 'hi-IN', mr: 'mr-IN' }[language], rate: .95,
+    try { await Speech.speak(message.content.replace(/\[S\d+\]/g, ''), {
+      language: { en: 'en-IN', hi: 'hi-IN', mr: 'mr-IN' }[message.language ?? language], rate: .95,
       onDone: () => setSpeaking(null), onStopped: () => setSpeaking(null),
       onError: () => { setSpeaking(null); setError('Speech playback failed. Check the installed voices and phone volume.'); },
-    });
+    }); } catch (err) { setSpeaking(null); setError(err instanceof Error ? err.message : 'Speech playback failed.'); }
   }
   return <KeyboardAvoidingView style={ui.screen} behavior={Platform.OS === 'ios' ? 'padding' : undefined} keyboardVerticalOffset={insets.top + 68}>
     <View style={[ui.row, { paddingHorizontal: 20, paddingTop: 12, justifyContent: 'space-between' }]}>
@@ -66,15 +65,15 @@
         </View>}
       </View>)}
       {busy && <View style={ui.row}><ActivityIndicator color={colors.primary} /><Text style={ui.subtitle}>{t.thinking}</Text></View>}
-      {!!(error || voice.error) && <View style={[ui.card, { backgroundColor: colors.redSoft }]}><Text accessibilityRole="alert" style={ui.error}>{error || voice.error}</Text>{needsLogin && <Pressable style={ui.button} onPress={() => router.push('/account')}><Text style={ui.buttonText}>{t.signIn}</Text></Pressable>}</View>}
+      {!!(error || voice.error) && <View style={[ui.card, { backgroundColor: colors.redSoft }]}><Text accessibilityRole="alert" style={ui.error}>{error || voice.error}</Text></View>}
       <Text style={ui.small}>{t.privacy}</Text>
     </ScrollView>
     <View style={styles.composer}>
       {(voice.recording || voice.processing) && <Text accessibilityLiveRegion="polite" style={[ui.small, { color: colors.primary }]}>{voice.recording ? `${t.recording} · ${voice.seconds}s / 60s` : t.transcribing}</Text>}
       <View style={[ui.row, { alignItems: 'flex-end' }]}>
-        <Pressable disabled={busy || voice.processing || !authReady} style={[styles.iconButton, { backgroundColor: voice.recording ? colors.red : colors.soft }]} accessibilityRole="button" accessibilityLabel={voice.recording ? t.stop : t.mic} onPress={() => { void Speech.stop(); setSpeaking(null); void voice.toggle(); }}><Ionicons name={voice.recording ? 'stop' : 'mic-outline'} size={23} color={voice.recording ? 'white' : colors.primary} /></Pressable>
+        <Pressable disabled={busy || voice.processing || !ready} style={[styles.iconButton, { backgroundColor: voice.recording ? colors.red : colors.soft }]} accessibilityRole="button" accessibilityLabel={voice.recording ? t.stop : t.mic} onPress={() => { void Speech.stop(); setSpeaking(null); void voice.toggle(); }}><Ionicons name={voice.recording ? 'stop' : 'mic-outline'} size={23} color={voice.recording ? 'white' : colors.primary} /></Pressable>
         <TextInput value={draft} onChangeText={setDraft} multiline maxLength={2500} editable={!busy && !voice.recording && !voice.processing} placeholder={t.ask} placeholderTextColor={colors.muted} accessibilityLabel={t.ask} style={styles.input} />
-        <Pressable disabled={!draft.trim() || busy || voice.recording || voice.processing || !authReady} onPress={send} accessibilityRole="button" accessibilityLabel={t.send} style={[styles.iconButton, { backgroundColor: colors.primary, opacity: !draft.trim() || busy || voice.recording || voice.processing ? .4 : 1 }]}><Ionicons name="arrow-up" size={24} color="white" /></Pressable>
+        <Pressable disabled={!draft.trim() || busy || voice.recording || voice.processing || !ready} onPress={send} accessibilityRole="button" accessibilityLabel={t.send} style={[styles.iconButton, { backgroundColor: colors.primary, opacity: !draft.trim() || busy || voice.recording || voice.processing ? .4 : 1 }]}><Ionicons name="arrow-up" size={24} color="white" /></Pressable>
       </View>
       <Text style={[ui.small, { fontSize: 10, textAlign: 'center' }]}>{t.note}</Text>
     </View>
```

### mobile/src/app/account.tsx

```diff
--- before/mobile/src/app/account.tsx
+++ after/mobile/src/app/account.tsx
@@ -1,25 +1,16 @@
-import { useState } from 'react';
-import { ActivityIndicator, Pressable, ScrollView, Text, View } from 'react-native';
+import { Pressable, ScrollView, Text, View } from 'react-native';
 import { router } from 'expo-router';
 import { Ionicons } from '@expo/vector-icons';
 import { useApp } from '../context/AppContext';
 import { colors, ui } from '../theme';
 export default function AccountScreen() {
-  const { user, signIn, signOut, t, authReady, authError } = useApp();
-  const [busy, setBusy] = useState(false); const [error, setError] = useState('');
-  async function act(fn: () => Promise<void>) {
-    setBusy(true); setError('');
-    try { await fn(); } catch (err) { setError(err instanceof Error ? err.message : 'Sign-in failed.'); } finally { setBusy(false); }
-  }
+  const { setMessages, t } = useApp();
   return <ScrollView style={ui.screen} contentContainerStyle={ui.content}>
     <Ionicons name="shield-checkmark-outline" size={56} color={colors.primary} />
-    <Text style={ui.title}>{user ? user.name : t.account}</Text><Text style={ui.subtitle}>{user ? user.email : t.accountIntro}</Text>
+    <Text style={ui.title}>{t.account}</Text><Text style={ui.subtitle}>{t.accountIntro}</Text>
     <View style={ui.card}>
-      {!authReady || busy ? <ActivityIndicator color={colors.primary} /> : user ?
-        <Pressable style={ui.button} onPress={() => act(signOut)} accessibilityRole="button"><Text style={ui.buttonText}>{t.signOut}</Text></Pressable> :
-        <Pressable style={[ui.button, { backgroundColor: 'white', borderWidth: 1, borderColor: colors.line }]} onPress={() => act(signIn)} accessibilityRole="button"><Ionicons name="logo-google" size={20} color={colors.ink} /><Text style={[ui.buttonText, { color: colors.ink }]}>{t.signIn}</Text></Pressable>}
-      {!!(error || authError) && <Text accessibilityRole="alert" style={ui.error}>{error || authError}</Text>}
-      <Pressable onPress={() => router.back()} accessibilityRole="button" style={[ui.button, { backgroundColor: colors.soft }]}><Text style={[ui.buttonText, { color: colors.primary }]}>{user ? t.close : t.guest}</Text></Pressable>
+      <Pressable style={[ui.button, { backgroundColor: 'white', borderWidth: 1, borderColor: colors.line }]} onPress={() => { setMessages([]); router.back(); }} accessibilityRole="button"><Ionicons name="chatbubble-outline" size={20} color={colors.ink} /><Text style={[ui.buttonText, { color: colors.ink }]}>{t.clearChat}</Text></Pressable>
+      <Pressable onPress={() => router.back()} accessibilityRole="button" style={[ui.button, { backgroundColor: colors.soft }]}><Text style={[ui.buttonText, { color: colors.primary }]}>{t.guest}</Text></Pressable>
     </View>
     <Text style={ui.subtitle}>{t.session}</Text><Text style={ui.small}>{t.privacy}</Text><Text style={ui.small}>{t.note}</Text>
   </ScrollView>;
```

### mobile/src/components/Header.tsx

```diff
--- before/mobile/src/components/Header.tsx
+++ after/mobile/src/components/Header.tsx
@@ -6,13 +6,13 @@
 import { colors } from '../theme';
 import { Language } from '../types';
 export function Header() {
-  const { language, setLanguage, t, user } = useApp();
+  const { language, setLanguage, t } = useApp();
   const insets = useSafeAreaInsets();
   return <View style={[styles.header, { paddingTop: insets.top + 10 }]}>
     <View style={styles.brand}><View style={styles.mark}><Ionicons name="shield-checkmark-outline" size={23} color="white" /></View><Text style={styles.name}>Naaya<Text style={{ color: colors.primary }}> AI</Text></Text></View>
     <View style={styles.actions}>
       {(['en', 'hi', 'mr'] as Language[]).map(lang => <Pressable key={lang} onPress={() => setLanguage(lang)} accessibilityRole="button" accessibilityLabel={{ en: 'English', hi: 'Hindi', mr: 'Marathi' }[lang]} accessibilityState={{ selected: lang === language }} style={[styles.lang, lang === language && { backgroundColor: colors.soft }]}><Text style={{ color: lang === language ? colors.primary : colors.muted, fontWeight: '600' }}>{{ en: 'EN', hi: 'हि', mr: 'म' }[lang]}</Text></Pressable>)}
-      <Pressable accessibilityRole="button" accessibilityLabel={t.account} onPress={() => router.push('/account')} style={styles.lang}><Ionicons name={user ? 'person-circle' : 'person-circle-outline'} size={29} color={colors.primary} /></Pressable>
+      <Pressable accessibilityRole="button" accessibilityLabel={t.account} onPress={() => router.push('/account')} style={styles.lang}><Ionicons name="person-circle-outline" size={29} color={colors.primary} /></Pressable>
     </View>
   </View>;
 }
```

### mobile/src/context/AppContext.tsx

```diff
--- before/mobile/src/context/AppContext.tsx
+++ after/mobile/src/context/AppContext.tsx
@@ -1,47 +1,34 @@
-import React, { createContext, useContext, useEffect, useState } from 'react';
+import React, { createContext, useContext, useEffect, useRef, useState } from 'react';
 import * as SecureStore from 'expo-secure-store';
-import { api, ApiError } from '../services/api';
-import { googleSignOut, googleToken } from '../services/google';
-import { Language, Message, User } from '../types';
+import { Language, Message } from '../types';
 import { copy } from '../data/uiText';
 
 function useAppState() {
-  const [language, setLanguage] = useState<Language>('en');
+  const [language, updateLanguage] = useState<Language>('en');
   const [messages, setMessages] = useState<Message[]>([]);
-  const [token, setToken] = useState<string | null>(null);
-  const [user, setUser] = useState<User | null>(null);
-  const [authReady, setAuthReady] = useState(false);
-  const [authError, setAuthError] = useState('');
+  const [ready, setReady] = useState(false);
+  const changed = useRef(false);
+  const writes = useRef(Promise.resolve());
   useEffect(() => {
     let active = true;
     (async () => {
       try {
-        const stored = await SecureStore.getItemAsync('naaya-session');
-        if (stored) {
-          const profile = await api.me(stored);
-          if (active) { setToken(stored); setUser(profile); }
-        }
-      } catch (error) {
-        if (error instanceof ApiError && error.status === 401) await SecureStore.deleteItemAsync('naaya-session');
-        if (active) setAuthError(error instanceof Error ? error.message : 'Unable to restore session.');
-      } finally { if (active) setAuthReady(true); }
+        // Remove a legacy session on upgrades; no account/session is used now.
+        await SecureStore.deleteItemAsync('naaya-session');
+        const value = await SecureStore.getItemAsync('naaya-language');
+        if (active && !changed.current && (value === 'en' || value === 'hi' || value === 'mr')) updateLanguage(value);
+      } catch { /* Device storage is optional. The app remains usable. */ }
+      finally { if (active) setReady(true); }
     })();
     return () => { active = false; };
   }, []);
-  async function signIn() {
-    setAuthError('');
-    const idToken = await googleToken();
-    if (!idToken) return;
-    const result = await api.login(idToken);
-    await SecureStore.setItemAsync('naaya-session', result.token);
-    setToken(result.token); setUser(result.user); setMessages([]);
+  function setLanguage(value: Language) {
+    changed.current = true;
+    updateLanguage(value);
+    // Serialize rapid taps so an older disk write cannot overwrite the last choice.
+    writes.current = writes.current.then(() => SecureStore.setItemAsync('naaya-language', value)).catch(() => undefined);
   }
-  async function signOut() {
-    await SecureStore.deleteItemAsync('naaya-session');
-    setToken(null); setUser(null); setMessages([]); setAuthError('');
-    await googleSignOut().catch(() => undefined);
-  }
-  return { language, setLanguage, t: copy[language], messages, setMessages, user, token, authReady, authError, signIn, signOut };
+  return { language, setLanguage, t: copy[language], messages, setMessages, ready };
 }
 const AppContext = createContext<ReturnType<typeof useAppState> | null>(null);
 export function AppProvider({ children }: React.PropsWithChildren) {
```

### mobile/src/data/uiText.ts

```diff
--- before/mobile/src/data/uiText.ts
+++ after/mobile/src/data/uiText.ts
@@ -14,9 +14,9 @@
   emergencyTitle: 'Help, when\nit matters.', emergencyIntro: 'Tap a number to open your phone’s dialler. Your phone may ask you to confirm the call.',
   emergency112: 'National emergency response', danger: 'Police, fire and medical emergencies', call: 'Call',
   source: 'Official information', coverage: 'Some services have limited hours or state coverage. Use 112 for immediate danger.',
-  signIn: 'Continue with Google', guest: 'Continue as guest', signOut: 'Sign out',
-  accountIntro: 'Sign in to use the assistant on servers that require an account. Portal links and emergency contacts are always available.',
-  session: 'Chats stay in memory for this session. Closing the app clears the conversation. Google login does not sync chat history.',
+  clearChat: 'Clear this chat', guest: 'Continue to assistant',
+  accountIntro: 'The assistant, portal links and emergency contacts work without an account.',
+  session: 'Chats stay in memory for this session. Closing the app clears the conversation. Your language choice is saved on this device.',
 };
 type Copy = { [K in keyof typeof en]: string };
 const hi: Copy = { ...en,
@@ -28,8 +28,8 @@
   portalTitle: 'अपनी बात\nसही जगह रखें।', portalIntro: 'केंद्र सरकार और राष्ट्रीय सेवाओं के 18 चुनिंदा शिकायत पोर्टल। लिंक आधिकारिक वेबसाइट खोलते हैं।',
   search: 'सेवा या समस्या खोजें…', open: 'आधिकारिक वेबसाइट खोलें', empty: 'कोई सेवा नहीं मिली। दूसरा शब्द खोजें।',
   emergencyTitle: 'ज़रूरत पर\nतुरंत सहायता।', emergencyIntro: 'नंबर दबाने पर फ़ोन का डायलर खुलेगा। फ़ोन कॉल की पुष्टि माँग सकता है।', emergency112: 'राष्ट्रीय आपातकालीन सहायता', danger: 'पुलिस, अग्निशमन और चिकित्सा आपातकाल', call: 'कॉल', source: 'आधिकारिक जानकारी',
-  coverage: 'कुछ सेवाओं के समय और राज्य में उपलब्धता अलग हैं। तत्काल खतरे में 112 पर कॉल करें।', signIn: 'Google से जारी रखें', guest: 'अतिथि के रूप में जारी रखें', signOut: 'साइन आउट',
-  accountIntro: 'जहाँ खाता आवश्यक है, वहाँ सहायक इस्तेमाल करने के लिए साइन इन करें। पोर्टल और आपातकालीन नंबर हमेशा उपलब्ध हैं।', session: 'चैट इस सत्र की मेमोरी में रहती है। ऐप बंद करने पर चैट हट जाती है। Google लॉगिन चैट को सिंक नहीं करता।',
+  coverage: 'कुछ सेवाओं के समय और राज्य में उपलब्धता अलग हैं। तत्काल खतरे में 112 पर कॉल करें।', clearChat: 'यह चैट हटाएँ', guest: 'सहायक पर जाएँ',
+  accountIntro: 'सहायक, पोर्टल और आपातकालीन नंबर बिना खाते के उपलब्ध हैं।', session: 'चैट इस सत्र की मेमोरी में रहती है। ऐप बंद करने पर चैट हट जाती है। भाषा इस डिवाइस पर सेव होती है।',
 };
 const mr: Copy = { ...en,
   assistant: 'सहाय्यक', portals: 'पोर्टल', emergency: 'आपत्कालीन', account: 'खाते', greeting: 'तुमचे हक्क.\nतुमचे पुढचे पाऊल.',
@@ -39,7 +39,7 @@
   newChat: 'नवीन चॅट', sources: 'संदर्भ', read: 'ऐका', stopReading: 'ऐकणे थांबवा', close: 'बंद करा',
   portalTitle: 'तुमची बाजू\nयोग्य ठिकाणी मांडा.', portalIntro: 'केंद्र सरकार आणि राष्ट्रीय सेवांचे 18 निवडक तक्रार पोर्टल. लिंक अधिकृत संकेतस्थळ उघडतात.', search: 'सेवा किंवा समस्या शोधा…', open: 'अधिकृत संकेतस्थळ उघडा', empty: 'सेवा सापडली नाही. दुसरा शब्द शोधा.',
   emergencyTitle: 'गरजेच्या वेळी\nत्वरित मदत.', emergencyIntro: 'क्रमांक दाबल्यावर फोनचा डायलर उघडतो. फोन कॉलची पुष्टी मागू शकतो.', emergency112: 'राष्ट्रीय आपत्कालीन मदत', danger: 'पोलीस, अग्निशमन आणि वैद्यकीय आपत्काल', call: 'कॉल', source: 'अधिकृत माहिती',
-  coverage: 'काही सेवांच्या वेळा आणि राज्यातील उपलब्धता वेगळी आहे. तात्काळ धोक्यात 112 वापरा.', signIn: 'Google सह पुढे जा', guest: 'पाहुणे म्हणून पुढे जा', signOut: 'साइन आउट',
-  accountIntro: 'खाते आवश्यक असलेल्या सर्व्हरवर सहाय्यक वापरण्यासाठी साइन इन करा. पोर्टल आणि आपत्कालीन क्रमांक नेहमी उपलब्ध आहेत.', session: 'चॅट या सत्राच्या मेमरीत राहते. ॲप बंद केल्यावर चॅट मिटते. Google लॉगिन चॅट सिंक करत नाही.',
+  coverage: 'काही सेवांच्या वेळा आणि राज्यातील उपलब्धता वेगळी आहे. तात्काळ धोक्यात 112 वापरा.', clearChat: 'ही चॅट हटवा', guest: 'सहाय्यकाकडे जा',
+  accountIntro: 'सहाय्यक, पोर्टल आणि आपत्कालीन क्रमांक खात्याशिवाय उपलब्ध आहेत.', session: 'चॅट या सत्राच्या मेमरीत राहते. ॲप बंद केल्यावर चॅट मिटते. भाषा या डिव्हाइसवर जतन होते.',
 };
 export const copy: Record<Language, Copy> = { en, hi, mr };
```

### mobile/src/hooks/useVoiceInput.ts

```diff
--- before/mobile/src/hooks/useVoiceInput.ts
+++ after/mobile/src/hooks/useVoiceInput.ts
@@ -8,7 +8,7 @@
 function removeRecording(uri: string | null) {
   if (uri) { try { const file = new File(uri); if (file.exists) file.delete(); } catch { /* OS can already have removed the cache file. */ } }
 }
-export function useVoiceInput(language: Language, token: string | null, onTranscript: (text: string) => void) {
+export function useVoiceInput(language: Language, onTranscript: (text: string) => void) {
   const recorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);
   const state = useAudioRecorderState(recorder, 200);
   const [processing, setProcessing] = useState(false);
@@ -25,7 +25,7 @@
       await recorder.stop(); uri = recorder.uri;
       await setAudioModeAsync({ allowsRecording: false });
       if (send && uri) {
-        const result = await api.transcribe(uri, language, token);
+        const result = await api.transcribe(uri, language);
         if (current !== generation.current) return;
         if (!result.text) throw new Error('No speech was detected. Please try again.');
         onTranscript(result.text);
@@ -37,7 +37,7 @@
       await setAudioModeAsync({ allowsRecording: false }).catch(() => undefined);
       locked.current = false; setProcessing(false);
     }
-  }, [recorder, language, token, onTranscript]);
+  }, [recorder, language, onTranscript]);
   const cancel = useCallback(() => { generation.current += 1; void finish(false); }, [finish]);
   useEffect(() => {
     const subscription = AppState.addEventListener('change', status => { if (status === 'background') cancel(); });
```

### mobile/src/services/api.ts

```diff
--- before/mobile/src/services/api.ts
+++ after/mobile/src/services/api.ts
@@ -1,14 +1,15 @@
-import { ChatResponse, Language, Message, User } from '../types';
-export const API_URL = (process.env.EXPO_PUBLIC_API_URL ?? '').replace(/\/$/, '');
+import { ChatResponse, Language, Message } from '../types';
+export const API_URL = (process.env.EXPO_PUBLIC_API_URL ?? '').trim().replace(/\/+$/, '');
 export class ApiError extends Error { constructor(message: string, public status: number) { super(message); } }
-async function request<T>(path: string, token: string | null, body?: unknown, form?: FormData): Promise<T> {
+async function request<T>(path: string, body?: unknown, form?: FormData): Promise<T> {
   if (!/^https?:\/\//.test(API_URL)) throw new Error('Set EXPO_PUBLIC_API_URL in mobile/.env, then restart Expo.');
   const controller = new AbortController();
-  const timer = setTimeout(() => controller.abort(), 115000);
+  // Three serial local CPU stages can take several minutes on an i3.
+  const timer = setTimeout(() => controller.abort(), form ? 90000 : 810000);
   try {
     const response = await fetch(API_URL + path, {
       method: body || form ? 'POST' : 'GET', signal: controller.signal,
-      headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}), ...(body ? { 'Content-Type': 'application/json' } : {}) },
+      headers: body ? { 'Content-Type': 'application/json' } : {},
       body: form ?? (body ? JSON.stringify(body) : undefined),
     });
     const payload = await response.json().catch(() => ({}));
@@ -16,22 +17,19 @@
     return payload as T;
   } catch (error) {
     if (error instanceof ApiError) throw error;
-    if (error instanceof Error && error.name === 'AbortError') throw new Error('Request timed out. Please try again.');
+    if (error instanceof Error && error.name === 'AbortError') throw new Error('Request timed out. Check Ollama; local CPU processing can be slow.');
     throw new Error('Cannot reach the server. Check its address, your Wi-Fi and whether the backend is running.');
   } finally { clearTimeout(timer); }
 }
 export const api = {
-  chat: (messages: Message[], language: Language, token: string | null) => request<ChatResponse>('/api/chat', token, {
-    // Bound history consistently with the server. The UI retains the full conversation.
-    messages: messages.slice(-8).map(({ role, content }) => ({ role, content: content.slice(0, 2500) })), language,
+  chat: (messages: Message[], language: Language) => request<ChatResponse>('/api/chat', {
+    // Keep request content within the backend limit, preserving the latest question.
+    messages: messages.slice(-6).map(({ role, content }) => ({ role, content: content.slice(0, 2500) })), language,
   }),
-  login: (idToken: string) => request<{ token: string; user: User }>('/api/auth/google', null, { id_token: idToken }),
-  me: (token: string) => request<User>('/api/auth/me', token),
-  transcribe: (uri: string, language: Language, token: string | null) => {
+  transcribe: (uri: string, language: Language) => {
     const form = new FormData();
-    // React Native uses a file descriptor for multipart uploads, rather than a browser Blob.
     form.append('file', { uri, name: 'question.m4a', type: 'audio/m4a' } as unknown as Blob);
     form.append('language', language);
-    return request<{ text: string }>('/api/transcribe', token, undefined, form);
+    return request<{ text: string }>('/api/transcribe', undefined, form);
   },
 };
```

### mobile/src/types.ts

```diff
--- before/mobile/src/types.ts
+++ after/mobile/src/types.ts
@@ -1,5 +1,7 @@
 export type Language = 'en' | 'hi' | 'mr';
-export type User = { id: string; name: string; email: string };
-export type Source = { id: string; title: string; text: string; file: string };
-export type Message = { id: string; role: 'user' | 'assistant'; content: string; sources?: Source[] };
-export type ChatResponse = { answer: string; sources: Source[] };
+export type Source = { id: string; title: string; text: string; file: string; chunk_id: string; act_name: string; section_number: string | null; section_title: string; provision_type: string };
+export type Message = { id: string; role: 'user' | 'assistant'; content: string; language?: Language; sources?: Source[] };
+export type LegalSection = { source_id: string; act_name: string; section_number: string; provision_type: string; explanation: string; evidence: string; status: string };
+export type Contact = { id: string; name: string; scope: string; phone: string | null; url: string; checked_on: string };
+export type Guidance = { summary: string; steps: string[]; contact_ids: string[]; recording_note: string; follow_up: string };
+export type ChatResponse = { answer: string; language: Language; sources: Source[]; sections: LegalSection[]; guidance: Guidance | null; contacts: Contact[]; warnings: string[]; guidance_status: 'ok' | 'unavailable' };
```
