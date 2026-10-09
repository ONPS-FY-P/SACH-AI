import { StyleSheet } from 'react-native';
export const colors = { ink: '#172D33', muted: '#597077', primary: '#146C60', soft: '#E6F3EE',
  background: '#F5F6F2', white: '#FFFFFF', line: '#DDE5DF', red: '#B93732', redSoft: '#FFF0EE', gold: '#B88036' };
export const ui = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  content: { padding: 20, gap: 16, paddingBottom: 36 },
  title: { fontSize: 30, lineHeight: 37, fontWeight: '700', color: colors.ink },
  subtitle: { fontSize: 15, lineHeight: 23, color: colors.muted },
  label: { fontSize: 12, letterSpacing: 1.5, fontWeight: '700', color: colors.primary },
  card: { padding: 18, borderRadius: 20, backgroundColor: colors.white, borderWidth: 1, borderColor: colors.line, gap: 10 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  body: { fontSize: 16, lineHeight: 25, color: colors.ink },
  small: { fontSize: 12, lineHeight: 18, color: colors.muted },
  button: { minHeight: 48, paddingHorizontal: 18, paddingVertical: 12, backgroundColor: colors.primary, borderRadius: 14, alignItems: 'center', justifyContent: 'center', flexDirection: 'row', gap: 8 },
  buttonText: { color: colors.white, fontWeight: '600', fontSize: 15 },
  input: { minHeight: 50, backgroundColor: colors.white, borderWidth: 1, borderColor: colors.line, borderRadius: 14, padding: 14, fontSize: 16, color: colors.ink },
  error: { color: colors.red, fontSize: 14, lineHeight: 21 },
  pill: { paddingHorizontal: 14, paddingVertical: 10, borderRadius: 24, backgroundColor: colors.white, borderWidth: 1, borderColor: colors.line },
});
