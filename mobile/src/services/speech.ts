import * as NativeSpeech from 'expo-speech';
let generation = 0;
export async function stop() {
  generation += 1;
  await NativeSpeech.stop();
}
export async function speak(text: string, options: NativeSpeech.SpeechOptions) {
  const current = generation;
  const lang = (options.language ?? 'en-IN').split('-')[0].toLowerCase();
  const voices = await NativeSpeech.getAvailableVoicesAsync();
  if (current !== generation) return;
  const voice = voices.find(v => v.language.toLowerCase() === options.language?.toLowerCase())
    ?? voices.find(v => v.language.toLowerCase().split(/[-_]/)[0] === lang);
  if (!voice) throw new Error(`Install an ${lang === 'hi' ? 'Hindi' : lang === 'mr' ? 'Marathi' : 'English'} text-to-speech voice in your phone settings, then retry.`);
  const max = Math.min(NativeSpeech.maxSpeechInputLength || 3000, 3000);
  const chunks: string[] = [];
  let remaining = text.replace(/https?:\/\/\S+/g, '').trim();
  while (remaining.length) {
    let end = Math.min(max, remaining.length);
    if (end < remaining.length) {
      const boundary = remaining.lastIndexOf(' ', end);
      if (boundary > max / 2) end = boundary;
    }
    chunks.push(remaining.slice(0, end)); remaining = remaining.slice(end).trim();
  }
  function next(index: number) {
    if (current !== generation) return;
    if (index >= chunks.length) { options.onDone?.(); return; }
    NativeSpeech.speak(chunks[index], { ...options, voice: voice!.identifier,
      onDone: () => next(index + 1),
      onStopped: () => { if (current === generation) options.onStopped?.(); },
      onError: error => { if (current === generation) options.onError?.(error); },
    });
  }
  next(0);
}
