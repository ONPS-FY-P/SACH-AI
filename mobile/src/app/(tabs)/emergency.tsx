import { Pressable, ScrollView, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { contacts } from '../../data/directory';
import { contactText } from '../../data/translations';
import { useApp } from '../../context/AppContext';
import { colors, ui } from '../../theme';
import { dial, openWebsite } from '../../services/links';
export default function EmergencyScreen() {
  const { t, language } = useApp();
  return <ScrollView style={ui.screen} contentContainerStyle={ui.content}>
    <Text style={[ui.label, { color: colors.red }]}>EMERGENCY & SUPPORT</Text><Text style={ui.title}>{t.emergencyTitle}</Text><Text style={ui.subtitle}>{t.emergencyIntro}</Text>
    <Pressable accessibilityRole="button" accessibilityLabel={`${t.call} 112: ${t.emergency112}`} onPress={() => dial('112')} style={[ui.card, { backgroundColor: colors.red, borderColor: colors.red }]}>
      <View style={ui.row}><Ionicons name="call" size={28} color="white" /><Text style={[ui.buttonText, { flex: 1 }]}>{t.emergency112}</Text></View>
      <Text style={{ color: 'white', fontSize: 58, fontWeight: '700' }}>112</Text><Text style={{ color: 'white', fontSize: 15 }}>{t.danger}</Text>
    </Pressable>
    <Text style={ui.small}>{t.coverage}</Text>
    {contacts.map(c => {
      const translated = language === 'en' ? [c.name, c.description] : contactText[c.number][language];
      return <View key={c.number} style={ui.card}>
        <View style={ui.row}><Text style={[ui.body, { flex: 1, fontWeight: '700' }]}>{translated[0]}</Text><Text style={{ color: colors.primary, fontSize: 23, fontWeight: '700' }}>{c.number}</Text></View>
        <Text style={ui.subtitle}>{translated[1]}</Text>
        <View style={ui.row}><Pressable onPress={() => dial(c.number)} accessibilityRole="button" accessibilityLabel={`${t.call} ${c.number}`} style={[ui.button, { flex: 1 }]}><Ionicons name="call-outline" size={18} color="white" /><Text style={ui.buttonText}>{t.call} {c.number}</Text></Pressable>
          <Pressable onPress={() => openWebsite(c.source)} accessibilityRole="link" accessibilityLabel={t.source} style={{ padding: 14 }}><Ionicons name="information-circle-outline" size={25} color={colors.muted} /></Pressable></View>
      </View>;
    })}
    <Pressable onPress={() => openWebsite('https://112.gov.in/')} accessibilityRole="link"><Text style={ui.small}>112 · {t.source} ↗</Text></Pressable>
  </ScrollView>;
}
