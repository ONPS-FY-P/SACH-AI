import { Alert, Linking } from 'react-native';
export async function openWebsite(url: string) {
  try { await Linking.openURL(url); }
  catch { Alert.alert('Unable to open link', 'Open this address in your browser: ' + url); }
}
export async function dial(number: string) {
  try { await Linking.openURL('tel:' + number); }
  catch { Alert.alert('Unable to open the dialler', 'Dial ' + number + ' on a phone. Simulators may not support calling.'); }
}
