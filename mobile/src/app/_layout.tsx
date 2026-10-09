import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { AppProvider } from '../context/AppContext';
import { colors } from '../theme';
export default function RootLayout() {
  return <SafeAreaProvider><AppProvider><StatusBar style="dark" /><Stack screenOptions={{ headerTintColor: colors.primary, contentStyle: { backgroundColor: colors.background } }}>
    <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
    <Stack.Screen name="account" options={{ presentation: 'modal', title: 'Naaya · Account' }} />
  </Stack></AppProvider></SafeAreaProvider>;
}
