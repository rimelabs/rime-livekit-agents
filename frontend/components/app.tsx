'use client';

import { useEffect, useMemo, useState } from 'react';
import { Room, RoomEvent } from 'livekit-client';
import { Settings, X } from 'lucide-react';
import { motion } from 'motion/react';
import { RoomAudioRenderer, RoomContext, StartAudio } from '@livekit/components-react';
import { AISettingsPanel } from '@/components/ai-settings-panel';
import { toastAlert } from '@/components/alert-toast';
import { SessionView } from '@/components/session-view';
import { Toaster } from '@/components/ui/sonner';
import { Welcome } from '@/components/welcome';
import useConnectionDetails from '@/hooks/useConnectionDetails';
import type { AppConfig } from '@/lib/types';

const MotionWelcome = motion.create(Welcome);
const MotionSessionView = motion.create(SessionView);

interface AppProps {
  appConfig: AppConfig;
}

export function App({ appConfig }: AppProps) {
  const room = useMemo(() => new Room(), []);
  const [sessionStarted, setSessionStarted] = useState(true);
  const { connectionDetails, refreshConnectionDetails } = useConnectionDetails();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    const onDisconnected = () => {
      setSessionStarted(true);
      refreshConnectionDetails();
    };
    const onMediaDevicesError = (error: Error) => {
      toastAlert({
        title: 'Encountered an error with your media devices',
        description: `${error.name}: ${error.message}`,
      });
    };
    room.on(RoomEvent.MediaDevicesError, onMediaDevicesError);
    room.on(RoomEvent.Disconnected, onDisconnected);
    return () => {
      room.off(RoomEvent.Disconnected, onDisconnected);
      room.off(RoomEvent.MediaDevicesError, onMediaDevicesError);
    };
  }, [room, refreshConnectionDetails]);

  useEffect(() => {
    let aborted = false;
    if (sessionStarted && room.state === 'disconnected' && connectionDetails) {
      Promise.all([
        room.localParticipant.setMicrophoneEnabled(true, undefined, {
          preConnectBuffer: appConfig.isPreConnectBufferEnabled,
        }),
        room.connect(connectionDetails.serverUrl, connectionDetails.participantToken),
      ]).catch((error) => {
        if (aborted) {
          // Once the effect has cleaned up after itself, drop any errors
          //
          // These errors are likely caused by this effect rerunning rapidly,
          // resulting in a previous run `disconnect` running in parallel with
          // a current run `connect`
          return;
        }

        toastAlert({
          title: 'There was an error connecting to the agent',
          description: `${error.name}: ${error.message}`,
        });
      });
    }
    return () => {
      aborted = true;
      room.disconnect();
    };
  }, [room, sessionStarted, connectionDetails, appConfig.isPreConnectBufferEnabled]);

  const { startButtonText } = appConfig;

  return (
    <>
      <MotionWelcome
        key="welcome"
        startButtonText={startButtonText}
        onStartCall={() => setSessionStarted(true)}
        disabled={sessionStarted}
        initial={{ opacity: 0 }}
        animate={{ opacity: sessionStarted ? 0 : 1 }}
        transition={{ duration: 0.5, ease: 'linear', delay: sessionStarted ? 0 : 0.5 }}
      />

      <RoomContext.Provider value={room}>
        <RoomAudioRenderer />
        <StartAudio label="Start Audio" />
        {/* --- */}
        <div className="flex flex-row">
          <div className="relative flex-1">
            <MotionSessionView
              key="session-view"
              appConfig={appConfig}
              disabled={!sessionStarted}
              sessionStarted={sessionStarted}
              initial={{ opacity: 0 }}
              animate={{ opacity: sessionStarted ? 1 : 0 }}
              transition={{
                duration: 0.5,
                ease: 'linear',
                delay: sessionStarted ? 0.5 : 0,
              }}
            />
          </div>
          <div>
            {!sidebarOpen && (
              <div className="cursor-pointer p-4" onClick={() => setSidebarOpen(true)}>
                <Settings />
              </div>
            )}
            {sidebarOpen && (
              <div className="bg-background relative z-50 flex h-screen w-screen flex-col md:w-[400px]">
                <div className="flex h-[50px] w-full items-center justify-end pr-3">
                  <button
                    onClick={() => setSidebarOpen(false)}
                    className="h-6 w-6 cursor-pointer rounded-4xl hover:bg-gray-100 hover:text-gray-500"
                    aria-label="Close sidebar"
                  >
                    <X className="h-5" />
                  </button>
                </div>
                <div className="h-[calc(100vh-50px)] overflow-auto">
                  <AISettingsPanel />
                </div>
              </div>
            )}
          </div>
        </div>
      </RoomContext.Provider>

      <Toaster />
    </>
  );
}
