import { useCallback, useRef, useState } from 'react';
import { ActivityIndicator, KeyboardAvoidingView, Modal, Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from 'expo-router';
import * as Speech from '../../services/speech';
import { SafeAreaView, useSafeAreaInsets } from 'react-native-safe-area-context';
import { useApp } from '../../context/AppContext';
import { useVoiceInput } from '../../hooks/useVoiceInput';
import { api } from '../../services/api';
import { Message, Source } from '../../types';
import { colors, ui } from '../../theme';

const ideas = {
  en: ['I lost money in an online scam', 'My order arrived damaged', 'What does Article 21 protect?'],
  hi: ['ऑनलाइन धोखाधड़ी में मेरे पैसे गए', 'मेरा सामान खराब आया है', 'अनुच्छेद 21 क्या सुरक्षा देता है?'],
  mr: ['ऑनलाइन फसवणुकीत माझे पैसे गेले', 'माझी वस्तू खराब आली आहे', 'अनुच्छेद 21 काय संरक्षण देतो?'],
};
export default function ChatScreen() {
  const { language, t, messages, setMessages, ready } = useApp();
  const [draft, setDraft] = useState(''); const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [sources, setSources] = useState<Source[] | null>(null); const [speaking, setSpeaking] = useState<string | null>(null);
  const scroll = useRef<ScrollView>(null); const sending = useRef(false); const insets = useSafeAreaInsets();
  const voice = useVoiceInput(language, setDraft);
  const cancelVoice = voice.cancel;
  useFocusEffect(useCallback(() => () => { cancelVoice(); void Speech.stop(); setSpeaking(null); }, [cancelVoice]));
  async function send() {
    const text = draft.trim(); if (!text || sending.current || voice.recording || voice.processing) return;
    sending.current = true; setBusy(true); setError(''); setDraft(''); void Speech.stop(); setSpeaking(null);
    const outgoing: Message = { id: Date.now().toString(), role: 'user', content: text, language };
    const next = [...messages, outgoing]; setMessages(next);
    try {
      const result = await api.chat(next, language);
      const incoming: Message = { id: `${Date.now()}-reply`, role: 'assistant', content: result.answer, sources: result.sources, language: result.language };
      setMessages(prev => prev.at(-1)?.id === outgoing.id ? [...prev, incoming] : prev);
    } catch (err) {
      setMessages(prev => prev.filter(m => m.id !== outgoing.id)); setDraft(text);
      setError(err instanceof Error ? err.message : 'Unable to get a response.');
    } finally { setBusy(false); sending.current = false; }
  }
  async function read(message: Message) {
    await Speech.stop();
    if (speaking === message.id) { setSpeaking(null); return; }
    setSpeaking(message.id);
    try { await Speech.speak(message.content.replace(/\[S\d+\]/g, ''), {
      language: { en: 'en-IN', hi: 'hi-IN', mr: 'mr-IN' }[message.language ?? language], rate: .95,
      onDone: () => setSpeaking(null), onStopped: () => setSpeaking(null),
      onError: () => { setSpeaking(null); setError('Speech playback failed. Check the installed voices and phone volume.'); },
    }); } catch (err) { setSpeaking(null); setError(err instanceof Error ? err.message : 'Speech playback failed.'); }
  }
  return <KeyboardAvoidingView style={ui.screen} behavior={Platform.OS === 'ios' ? 'padding' : undefined} keyboardVerticalOffset={insets.top + 68}>
    <View style={[ui.row, { paddingHorizontal: 20, paddingTop: 12, justifyContent: 'space-between' }]}>
      <Text style={ui.label}>LEGAL GUIDANCE</Text><Pressable disabled={busy || voice.recording || voice.processing} accessibilityRole="button" onPress={() => { setMessages([]); setError(''); setDraft(''); void Speech.stop(); setSpeaking(null); }} style={{ padding: 10 }}><Text style={{ color: colors.primary, fontWeight: '600' }}>{t.newChat} +</Text></Pressable>
    </View>
    <ScrollView ref={scroll} keyboardShouldPersistTaps="handled" contentContainerStyle={[ui.content, { paddingTop: 8 }]} onContentSizeChange={() => { if (messages.length) scroll.current?.scrollToEnd({ animated: true }); }}>
      {!messages.length && <>
        <View style={styles.hero}><View style={styles.emblem}><Ionicons name="sparkles-outline" size={30} color={colors.primary} /></View><Text style={ui.title}>{t.greeting}</Text><Text style={ui.subtitle}>{t.intro}</Text></View>
        {ideas[language].map(idea => <Pressable key={idea} accessibilityRole="button" onPress={() => setDraft(idea)} style={[ui.card, ui.row]}><Text style={[ui.body, { flex: 1 }]}>{idea}</Text><Ionicons name="arrow-forward" size={19} color={colors.primary} /></Pressable>)}
      </>}
      {messages.map(message => <View key={message.id} style={[styles.bubble, message.role === 'user' ? styles.user : styles.assistant]}>
        <Text selectable style={[ui.body, message.role === 'user' && { color: 'white' }]}>{message.content}</Text>
        {message.role === 'assistant' && <View style={[ui.row, { flexWrap: 'wrap', marginTop: 10 }]}>
          {!!message.sources?.length && <Pressable style={ui.pill} onPress={() => setSources(message.sources!)} accessibilityRole="button"><Text style={{ color: colors.primary }}>{t.sources} · {message.sources.length}</Text></Pressable>}
          <Pressable disabled={voice.recording || voice.processing} style={ui.pill} onPress={() => read(message)} accessibilityRole="button" accessibilityLabel={speaking === message.id ? t.stopReading : t.read}><Ionicons name={speaking === message.id ? 'stop-circle-outline' : 'volume-medium-outline'} color={colors.primary} size={21} /></Pressable>
        </View>}
      </View>)}
      {busy && <View style={ui.row}><ActivityIndicator color={colors.primary} /><Text style={ui.subtitle}>{t.thinking}</Text></View>}
      {!!(error || voice.error) && <View style={[ui.card, { backgroundColor: colors.redSoft }]}><Text accessibilityRole="alert" style={ui.error}>{error || voice.error}</Text></View>}
      <Text style={ui.small}>{t.privacy}</Text>
    </ScrollView>
    <View style={styles.composer}>
      {(voice.recording || voice.processing) && <Text accessibilityLiveRegion="polite" style={[ui.small, { color: colors.primary }]}>{voice.recording ? `${t.recording} · ${voice.seconds}s / 60s` : t.transcribing}</Text>}
      <View style={[ui.row, { alignItems: 'flex-end' }]}>
        <Pressable disabled={busy || voice.processing || !ready} style={[styles.iconButton, { backgroundColor: voice.recording ? colors.red : colors.soft }]} accessibilityRole="button" accessibilityLabel={voice.recording ? t.stop : t.mic} onPress={() => { void Speech.stop(); setSpeaking(null); void voice.toggle(); }}><Ionicons name={voice.recording ? 'stop' : 'mic-outline'} size={23} color={voice.recording ? 'white' : colors.primary} /></Pressable>
        <TextInput value={draft} onChangeText={setDraft} multiline maxLength={2500} editable={!busy && !voice.recording && !voice.processing} placeholder={t.ask} placeholderTextColor={colors.muted} accessibilityLabel={t.ask} style={styles.input} />
        <Pressable disabled={!draft.trim() || busy || voice.recording || voice.processing || !ready} onPress={send} accessibilityRole="button" accessibilityLabel={t.send} style={[styles.iconButton, { backgroundColor: colors.primary, opacity: !draft.trim() || busy || voice.recording || voice.processing ? .4 : 1 }]}><Ionicons name="arrow-up" size={24} color="white" /></Pressable>
      </View>
      <Text style={[ui.small, { fontSize: 10, textAlign: 'center' }]}>{t.note}</Text>
    </View>
    <Modal visible={!!sources} animationType="slide" onRequestClose={() => setSources(null)}>
      <SafeAreaView style={ui.screen}><ScrollView contentContainerStyle={ui.content}>
        <View style={[ui.row, { justifyContent: 'space-between' }]}><Text style={ui.title}>{t.sources}</Text><Pressable style={ui.pill} onPress={() => setSources(null)} accessibilityRole="button"><Text>{t.close}</Text></Pressable></View>
        <Text style={ui.small}>Excerpts from the supplied reference collection. These may be incomplete or outdated; citations do not guarantee legal accuracy.</Text>
        {sources?.map(source => <View style={ui.card} key={source.id}><Text style={[ui.body, { fontWeight: '700' }]}>[{source.id}] {source.title}</Text><Text selectable style={ui.subtitle}>{source.text}</Text><Text style={ui.small}>{source.file}</Text></View>)}
      </ScrollView></SafeAreaView>
    </Modal>
  </KeyboardAvoidingView>;
}
const styles = StyleSheet.create({
  hero: { gap: 16, paddingVertical: 16 }, emblem: { backgroundColor: colors.soft, width: 62, height: 62, borderRadius: 22, justifyContent: 'center', alignItems: 'center' },
  bubble: { padding: 16, borderRadius: 20, maxWidth: '96%', gap: 4 }, user: { alignSelf: 'flex-end', backgroundColor: colors.primary, borderBottomRightRadius: 5 },
  assistant: { alignSelf: 'flex-start', backgroundColor: colors.white, borderWidth: 1, borderColor: colors.line, borderBottomLeftRadius: 5 },
  composer: { backgroundColor: colors.white, padding: 12, gap: 8, borderTopWidth: 1, borderTopColor: colors.line },
  input: { flex: 1, minHeight: 48, maxHeight: 125, backgroundColor: colors.background, paddingHorizontal: 12, paddingTop: 13, paddingBottom: 12, borderRadius: 14, color: colors.ink, fontSize: 16 },
  iconButton: { width: 48, height: 48, borderRadius: 16, alignItems: 'center', justifyContent: 'center' },
});
