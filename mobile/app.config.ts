import type { ExpoConfig, ConfigContext } from 'expo/config';
// app.json holds the static configuration, including the ID written by eas init.
export default ({ config }: ConfigContext): ExpoConfig => {
  const local = ['development', 'lan'].includes(process.env.APP_VARIANT ?? 'development');
  return {
    ...config,
    name: config.name ?? 'Naaya AI', slug: config.slug ?? 'naaya-mobile',
    ios: { ...config.ios, infoPlist: {
      ...config.ios?.infoPlist,
      ...(local ? { NSAppTransportSecurity: { NSAllowsLocalNetworking: true } } : {}),
    } },
    plugins: [...(config.plugins ?? []), ['expo-build-properties', { android: { usesCleartextTraffic: local } }]],
  };
};
