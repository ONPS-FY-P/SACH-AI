import { Pressable, ScrollView, Text, View } from 'react-native';
import { router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useApp } from '../context/AppContext';
import { colors, ui } from '../theme';
export default function AccountScreen() {
  const { setMessages, t } = useApp();
  return <ScrollView style={ui.screen} contentContainerStyle={ui.content}>
    <Ionicons name="shield-checkmark-outline" size={56} color={colors.primary} />
    <Text style={ui.title}>{t.account}</Text><Text style={ui.subtitle}>{t.accountIntro}</Text>
    <View style={ui.card}>
      <Pressable style={[ui.button, { backgroundColor: 'white', borderWidth: 1, borderColor: colors.line }]} onPress={() => { setMessages([]); router.back(); }} accessibilityRole="button"><Ionicons name="chatbubble-outline" size={20} color={colors.ink} /><Text style={[ui.buttonText, { color: colors.ink }]}>{t.clearChat}</Text></Pressable>
      <Pressable onPress={() => router.back()} accessibilityRole="button" style={[ui.button, { backgroundColor: colors.soft }]}><Text style={[ui.buttonText, { color: colors.primary }]}>{t.guest}</Text></Pressable>
    </View>
    <Text style={ui.subtitle}>{t.session}</Text><Text style={ui.small}>{t.privacy}</Text><Text style={ui.small}>{t.note}</Text>
  </ScrollView>;
}
