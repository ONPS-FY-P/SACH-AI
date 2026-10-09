import { useCallback, useEffect, useRef, useState } from 'react';
import { AppState } from 'react-native';
import { AudioModule, RecordingPresets, setAudioModeAsync, useAudioRecorder, useAudioRecorderState } from 'expo-audio';
import { File } from 'expo-file-system';
import { api } from '../services/api';
import { Language } from '../types';

function removeRecording(uri: string | null) {
  if (uri) { try { const file = new File(uri); if (file.exists) file.delete(); } catch { /* OS can already have removed the cache file. */ } }
}
export function useVoiceInput(language: Language, onTranscript: (text: string) => void) {
  const recorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);
  const state = useAudioRecorderState(recorder, 200);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState('');
  const active = useRef(false);
  const locked = useRef(false);
  const generation = useRef(0);
  const finish = useCallback(async (send: boolean) => {
    if (!active.current || locked.current) return;
    locked.current = true; active.current = false; setProcessing(true);
    const current = generation.current;
    let uri: string | null = null;
    try {
      await recorder.stop(); uri = recorder.uri;
      await setAudioModeAsync({ allowsRecording: false });
      if (send && uri) {
        const result = await api.transcribe(uri, language);
        if (current !== generation.current) return;
        if (!result.text) throw new Error('No speech was detected. Please try again.');
        onTranscript(result.text);
      }
    } catch (err) {
      if (send && current === generation.current) setError(err instanceof Error ? err.message : 'Recording failed.');
    } finally {
      removeRecording(uri ?? recorder.uri);
      await setAudioModeAsync({ allowsRecording: false }).catch(() => undefined);
      locked.current = false; setProcessing(false);
    }
  }, [recorder, language, onTranscript]);
  const cancel = useCallback(() => { generation.current += 1; void finish(false); }, [finish]);
  useEffect(() => {
    const subscription = AppState.addEventListener('change', status => { if (status === 'background') cancel(); });
    return () => subscription.remove();
  }, [cancel]);
  useEffect(() => { if (state.isRecording && state.durationMillis >= 60000) void finish(true); }, [state.isRecording, state.durationMillis, finish]);
  const toggle = async () => {
    setError('');
    if (locked.current) return;
    if (active.current) { await finish(true); return; }
    locked.current = true; setProcessing(true);
    const current = generation.current;
    try {
      const permission = await AudioModule.requestRecordingPermissionsAsync();
      if (!permission.granted) throw new Error('Microphone permission is off. Enable it in your phone settings, or type your question.');
      if (current !== generation.current || AppState.currentState !== 'active') return;
      await setAudioModeAsync({ allowsRecording: true, playsInSilentMode: true });
      await recorder.prepareToRecordAsync();
      if (current !== generation.current) { await recorder.stop(); removeRecording(recorder.uri); return; }
      recorder.record(); active.current = true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to access the microphone.');
    } finally {
      if (!active.current) await setAudioModeAsync({ allowsRecording: false }).catch(() => undefined);
      locked.current = false; setProcessing(false);
    }
  };
  return { recording: state.isRecording, seconds: Math.floor(state.durationMillis / 1000), processing, error, toggle, cancel };
}
