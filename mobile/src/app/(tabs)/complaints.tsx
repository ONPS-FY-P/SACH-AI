import { useState } from 'react';
import { Pressable, ScrollView, Text, TextInput, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { portals, categories, verifiedOn } from '../../data/directory';
import { categoryText, portalText } from '../../data/translations';
import { useApp } from '../../context/AppContext';
import { colors, ui } from '../../theme';
import { openWebsite } from '../../services/links';
export default function ComplaintScreen() {
  const { language, t } = useApp();
  const [query, setQuery] = useState(''); const [category, setCategory] = useState('All portals');
  const describe = (id: string, fallback: string) => language === 'en' ? fallback : (portalText[id]?.[language] ?? fallback);
  const visible = portals.filter(p => (category === 'All portals' || p.category === category) && `${p.title} ${p.agency} ${p.description} ${describe(p.id, p.description)} ${p.category}`.toLowerCase().includes(query.toLowerCase().trim()));
  return <ScrollView style={ui.screen} contentContainerStyle={ui.content} keyboardShouldPersistTaps="handled">
    <Text style={ui.label}>OFFICIAL SERVICES</Text><Text style={ui.title}>{t.portalTitle}</Text><Text style={ui.subtitle}>{t.portalIntro}</Text>
    <TextInput style={ui.input} value={query} onChangeText={setQuery} placeholder={t.search} placeholderTextColor={colors.muted} accessibilityLabel={t.search} />
    <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 8 }}>
      {categories.map(c => <Pressable key={c} onPress={() => setCategory(c)} accessibilityRole="button" accessibilityState={{ selected: c === category }} style={[ui.pill, c === category && { backgroundColor: colors.soft, borderColor: colors.primary }]}><Text style={{ color: colors.primary }}>{language === 'en' ? c : categoryText[c]?.[language] ?? c}</Text></Pressable>)}
    </ScrollView>
    {!visible.length && <Text style={ui.subtitle}>{t.empty}</Text>}
    {visible.map(p => <View style={ui.card} key={p.id}>
      <View style={ui.row}><Ionicons name="business-outline" size={22} color={colors.primary} /><Text style={[ui.body, { flex: 1, fontWeight: '700' }]}>{p.title}</Text><Ionicons name="checkmark-circle" size={18} color={colors.primary} /></View>
      <Text style={ui.small}>{p.agency}</Text><Text style={ui.subtitle}>{describe(p.id, p.description)}</Text>
      {p.note && <Text style={ui.small}>{p.note}</Text>}
      <Pressable onPress={() => openWebsite(p.url)} style={[ui.button, { backgroundColor: colors.soft }]} accessibilityRole="link" accessibilityLabel={`${t.open}: ${p.title}`}><Text style={[ui.buttonText, { color: colors.primary }]}>{t.open}</Text><Ionicons name="open-outline" size={17} color={colors.primary} /></Pressable>
    </View>)}
    <Text style={ui.small}>Directory reviewed {verifiedOn}. This is a curated starting list, not every government website. Naaya is an independent project, not a government service.</Text>
  </ScrollView>;
}
