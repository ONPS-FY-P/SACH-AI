import { Pressable, StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useApp } from '../context/AppContext';
import { colors } from '../theme';
import { Language } from '../types';
export function Header() {
  const { language, setLanguage, t } = useApp();
  const insets = useSafeAreaInsets();
  return <View style={[styles.header, { paddingTop: insets.top + 10 }]}>
    <View style={styles.brand}><View style={styles.mark}><Ionicons name="shield-checkmark-outline" size={23} color="white" /></View><Text style={styles.name}>Naaya<Text style={{ color: colors.primary }}> AI</Text></Text></View>
    <View style={styles.actions}>
      {(['en', 'hi', 'mr'] as Language[]).map(lang => <Pressable key={lang} onPress={() => setLanguage(lang)} accessibilityRole="button" accessibilityLabel={{ en: 'English', hi: 'Hindi', mr: 'Marathi' }[lang]} accessibilityState={{ selected: lang === language }} style={[styles.lang, lang === language && { backgroundColor: colors.soft }]}><Text style={{ color: lang === language ? colors.primary : colors.muted, fontWeight: '600' }}>{{ en: 'EN', hi: 'हि', mr: 'म' }[lang]}</Text></Pressable>)}
      <Pressable accessibilityRole="button" accessibilityLabel={t.account} onPress={() => router.push('/account')} style={styles.lang}><Ionicons name="person-circle-outline" size={29} color={colors.primary} /></Pressable>
    </View>
  </View>;
}
const styles = StyleSheet.create({
  header: { backgroundColor: colors.white, paddingHorizontal: 16, paddingBottom: 12, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', borderBottomWidth: 1, borderBottomColor: colors.line, gap: 6 },
  brand: { flexDirection: 'row', alignItems: 'center', gap: 7 }, mark: { backgroundColor: colors.primary, width: 34, height: 38, borderRadius: 12, alignItems: 'center', justifyContent: 'center' },
  name: { fontSize: 20, fontWeight: '700', color: colors.ink }, actions: { flexDirection: 'row', alignItems: 'center' },
  lang: { minWidth: 36, minHeight: 44, alignItems: 'center', justifyContent: 'center', borderRadius: 12 },
});
