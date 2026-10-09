import React, { createContext, useContext, useEffect, useRef, useState } from 'react';
import * as SecureStore from 'expo-secure-store';
import { Language, Message } from '../types';
import { copy } from '../data/uiText';

function useAppState() {
  const [language, updateLanguage] = useState<Language>('en');
  const [messages, setMessages] = useState<Message[]>([]);
  const [ready, setReady] = useState(false);
  const changed = useRef(false);
  const writes = useRef(Promise.resolve());
  useEffect(() => {
    let active = true;
    (async () => {
      try {
        // Remove a legacy session on upgrades; no account/session is used now.
        await SecureStore.deleteItemAsync('naaya-session');
        const value = await SecureStore.getItemAsync('naaya-language');
        if (active && !changed.current && (value === 'en' || value === 'hi' || value === 'mr')) updateLanguage(value);
      } catch { /* Device storage is optional. The app remains usable. */ }
      finally { if (active) setReady(true); }
    })();
    return () => { active = false; };
  }, []);
  function setLanguage(value: Language) {
    changed.current = true;
    updateLanguage(value);
    // Serialize rapid taps so an older disk write cannot overwrite the last choice.
    writes.current = writes.current.then(() => SecureStore.setItemAsync('naaya-language', value)).catch(() => undefined);
  }
  return { language, setLanguage, t: copy[language], messages, setMessages, ready };
}
const AppContext = createContext<ReturnType<typeof useAppState> | null>(null);
export function AppProvider({ children }: React.PropsWithChildren) {
  const value = useAppState();
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}
export function useApp() {
  const context = useContext(AppContext);
  if (!context) throw new Error('AppProvider is missing.');
  return context;
}
