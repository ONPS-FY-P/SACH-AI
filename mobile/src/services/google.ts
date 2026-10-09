import Constants, { ExecutionEnvironment } from 'expo-constants';
import { Platform } from 'react-native';
let configured = false;
export async function googleToken(): Promise<string | null> {
  if (Constants.executionEnvironment === ExecutionEnvironment.StoreClient) {
    throw new Error('Google login needs the development APK. Use guest mode in Expo Go. See the setup guide.');
  }
  if (!process.env.EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID) throw new Error('Add your Google Web client ID to mobile/.env.');
  if (Platform.OS === 'ios' && !process.env.EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID) throw new Error('Configure the iOS Google client and rebuild the app.');
  // Delay loading the native module so the other screens can run in Expo Go.
  const { GoogleSignin, isSuccessResponse } = await import('@react-native-google-signin/google-signin');
  if (!configured) {
    GoogleSignin.configure({ webClientId: process.env.EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID,
      iosClientId: process.env.EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID || undefined });
    configured = true;
  }
  await GoogleSignin.hasPlayServices({ showPlayServicesUpdateDialog: true });
  const result = await GoogleSignin.signIn();
  if (!isSuccessResponse(result)) return null;
  if (!result.data.idToken) throw new Error('No Google ID token. Check the Web client ID, package name and SHA-1 configuration.');
  return result.data.idToken;
}
export async function googleSignOut() {
  if (configured) { const { GoogleSignin } = await import('@react-native-google-signin/google-signin'); await GoogleSignin.signOut(); }
}
