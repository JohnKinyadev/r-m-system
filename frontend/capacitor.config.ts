import type { CapacitorConfig } from '@capacitor/cli'

const config: CapacitorConfig = {
  appId: 'com.farmmanagement.app',
  appName: 'FarmManager',
  webDir: 'dist',
  server: {
    // For development/testing on device, point to your server IP.
    // Remove this block for production Play Store builds.
    // url: 'http://192.168.1.x:5173',
    // cleartext: true,
  },
  plugins: {
    PushNotifications: {
      presentationOptions: ['badge', 'sound', 'alert'],
    },
    StatusBar: {
      style: 'dark',
      backgroundColor: '#1a5c2a',
    },
  },
}

export default config
