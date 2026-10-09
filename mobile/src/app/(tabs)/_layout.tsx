import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { View } from 'react-native';
import { Header } from '../../components/Header';
import { colors } from '../../theme';
import { useApp } from '../../context/AppContext';
export default function TabLayout() {
  const { t } = useApp();
  return <View style={{ flex: 1 }}><Header /><Tabs screenOptions={{ headerShown: false, tabBarActiveTintColor: colors.primary, tabBarInactiveTintColor: colors.muted, tabBarHideOnKeyboard: true, tabBarStyle: { borderTopColor: colors.line }, tabBarLabelStyle: { fontSize: 12, fontWeight: '600' } }}>
    <Tabs.Screen name="index" options={{ title: t.assistant, tabBarIcon: ({ color, size }) => <Ionicons name="chatbubble-ellipses-outline" color={color} size={size} /> }} />
    <Tabs.Screen name="complaints" options={{ title: t.portals, tabBarIcon: ({ color, size }) => <Ionicons name="business-outline" color={color} size={size} /> }} />
    <Tabs.Screen name="emergency" options={{ title: t.emergency, tabBarIcon: ({ color, size }) => <Ionicons name="call-outline" color={color} size={size} /> }} />
  </Tabs></View>;
}
