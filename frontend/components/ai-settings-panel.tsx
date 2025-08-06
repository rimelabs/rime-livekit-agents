'use client';

import * as React from 'react';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { AISettings, AgentType, ModelType } from '@/lib/types';
import { cn } from '@/lib/utils';

interface AISettingsPanelProps {
  aiSettings: AISettings;
  setAISettings: (settings: AISettings) => void;
  selectedAgent: AgentType;
  setSelectedAgent: (agent: AgentType) => void;
}

const arcanaVoices = [
  { value: 'luna', label: 'Luna' },
  { value: 'aria', label: 'Aria' },
  { value: 'nova', label: 'Nova' },
  { value: 'echo', label: 'Echo' },
];

const mistv2Voices = [
  { value: 'harry', label: 'Harry' },
  { value: 'ron', label: 'Ron' },
  { value: 'hermione', label: 'Hermione' },
  { value: 'ginny', label: 'Ginny' },
];

const prebuiltAgents = [
  { value: 'general', label: 'General' },
  { value: 'finance', label: 'Finance' },
  { value: 'legal', label: 'Legal' },
  { value: 'medical', label: 'Medical' },
  { value: 'tech', label: 'Tech' },
  { value: 'marketing', label: 'Marketing' },
];

const DEFAULT_ARCANA_SETTINGS = {
  voice: 'luna',
  temperature: 1,
  repetitionPenalty: 1,
  topP: 0.9,
};

const DEFAULT_MISTV2_SETTINGS = {
  voice: 'harry',
  speed: 1,
};

export const AISettingsPanel: React.FC<AISettingsPanelProps> = ({
  aiSettings,
  setAISettings,
  selectedAgent,
  setSelectedAgent,
}) => {
  // Get current model's settings
  const currentModelSettings =
    aiSettings.model === 'arcana' ? aiSettings.arcanaSettings : aiSettings.mistv2Settings;

  // Function to switch model
  const switchModel = (model: ModelType) => {
    setAISettings({
      ...aiSettings,
      model,
    });
  };

  // Function to update model-specific settings
  const updateModelSettings = (newSettings: Partial<typeof currentModelSettings>) => {
    if (aiSettings.model === 'arcana') {
      setAISettings({
        ...aiSettings,
        arcanaSettings: { ...aiSettings.arcanaSettings, ...newSettings },
      });
    } else {
      setAISettings({
        ...aiSettings,
        mistv2Settings: { ...aiSettings.mistv2Settings, ...newSettings },
      });
    }
  };

  return (
    <div className="bg-background text-foreground h-full space-y-8 p-6">
      {/* Model Section */}
      <div className="space-y-4">
        <h2 className="text-foreground text-xl font-semibold">Model:</h2>
        <div className="flex flex-row gap-3">
          <Card
            className={cn(
              'hover:border-border flex-1 cursor-pointer border transition-all duration-200',
              aiSettings.model === 'arcana'
                ? 'border-neutral-500 bg-gradient-to-tr from-neutral-800 via-neutral-600 to-neutral-800 shadow-lg'
                : 'text-card-foreground border-border bg-gradient-to-tr from-black via-neutral-700 to-black hover:border-neutral-500 hover:bg-gradient-to-tl hover:from-neutral-800 hover:via-neutral-600 hover:to-neutral-800 hover:shadow-lg'
            )}
            onClick={() => switchModel('arcana')}
          >
            <div className="p-4 text-center">
              <div className="mb-2 text-lg font-bold">ARCANA</div>
              <div className="text-sm opacity-80">Unmatched realism</div>
            </div>
          </Card>

          <Card
            className={cn(
              'hover:border-border flex-1 cursor-pointer border transition-all duration-200',
              aiSettings.model === 'mistv2'
                ? 'border-neutral-500 bg-gradient-to-tl from-neutral-800 via-neutral-600 to-neutral-800 shadow-lg'
                : 'text-card-foreground border-border bg-gradient-to-tl from-black via-neutral-700 to-black hover:border-neutral-500 hover:bg-gradient-to-tl hover:from-neutral-800 hover:via-neutral-600 hover:to-neutral-800 hover:shadow-lg'
            )}
            onClick={() => switchModel('mistv2')}
          >
            <div className="p-4 text-center">
              <div className="mb-2 text-lg font-bold">MIST V2</div>
              <div className="text-sm opacity-80">Speed and customizability</div>
            </div>
          </Card>
        </div>
      </div>

      {/* Voice Section */}
      <div className="space-y-4">
        <div className="space-y-1.5">
          <Label htmlFor="voice-select" className="text-xs font-medium">
            Select Voice
          </Label>
          <Select
            value={currentModelSettings.voice}
            onValueChange={(voice) => updateModelSettings({ voice })}
          >
            <SelectTrigger
              id="voice-select"
              className="w-full rounded-md border-neutral-700 bg-neutral-900 text-neutral-100 hover:bg-neutral-800 focus:ring-neutral-700"
            >
              <SelectValue placeholder="Select a voice" />
            </SelectTrigger>
            <SelectContent className="rounded-md border-neutral-700 bg-neutral-900 text-neutral-100">
              {(aiSettings?.model === 'arcana' ? arcanaVoices : mistv2Voices).map((voice) => (
                <SelectItem
                  key={voice.value}
                  value={voice.value}
                  className="text-popover-foreground hover:bg-accent hover:text-accent-foreground"
                >
                  {voice.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Agent Section */}
      <div className="space-y-4">
        <div className="space-y-1.5">
          <Label htmlFor="agent-select" className="text-xs font-medium">
            Select Agent
          </Label>
          <Select
            value={selectedAgent}
            onValueChange={(agent: AgentType) => setSelectedAgent(agent)}
          >
            <SelectTrigger
              id="agent-select"
              className="w-full rounded-md border-neutral-700 bg-neutral-900 text-neutral-100 hover:bg-neutral-800 focus:ring-neutral-700"
            >
              <SelectValue placeholder="Select an agent" />
            </SelectTrigger>
            <SelectContent className="rounded-md border-neutral-700 bg-neutral-900 text-neutral-100">
              {prebuiltAgents.map((agent) => (
                <SelectItem
                  key={agent.value}
                  value={agent.value}
                  className="text-popover-foreground hover:bg-accent hover:text-accent-foreground"
                >
                  {agent.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Settings Section */}
      <div className="space-y-6">
        {aiSettings.model === 'arcana' ? (
          <>
            {/* Temperature */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label className="text-foreground text-sm font-medium">Temperature</Label>
                <span className="text-foreground text-sm font-bold">
                  {currentModelSettings.temperature?.toFixed(2)}
                </span>
              </div>
              <Slider
                value={[currentModelSettings.temperature || DEFAULT_ARCANA_SETTINGS.temperature]}
                onValueChange={(value) => updateModelSettings({ temperature: value[0] })}
                max={2}
                min={0}
                step={0.01}
                className="w-full"
              />
              <div className="text-muted-foreground flex justify-between text-sm">
                <span>Lower</span>
                <span>Higher</span>
              </div>
            </div>

            {/* Repetition Penalty */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label className="text-foreground text-sm font-medium">Repetition Penalty</Label>
                <span className="text-foreground text-sm font-bold">
                  {currentModelSettings.repetitionPenalty?.toFixed(1)}
                </span>
              </div>
              <Slider
                value={[
                  currentModelSettings.repetitionPenalty ||
                    DEFAULT_ARCANA_SETTINGS.repetitionPenalty,
                ]}
                onValueChange={(value) => updateModelSettings({ repetitionPenalty: value[0] })}
                max={2}
                min={0}
                step={0.1}
                className="w-full"
              />
              <div className="text-muted-foreground flex justify-between text-sm">
                <span>Lower</span>
                <span>Higher</span>
              </div>
            </div>

            {/* Top P */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label className="text-foreground text-sm font-medium">Top P</Label>
                <span className="text-foreground text-sm font-bold">
                  {currentModelSettings.topP?.toFixed(2)}
                </span>
              </div>
              <Slider
                value={[currentModelSettings.topP || DEFAULT_ARCANA_SETTINGS.topP]}
                onValueChange={(value) => updateModelSettings({ topP: value[0] })}
                max={1}
                min={0}
                step={0.025}
                className="w-full"
              />
              <div className="text-muted-foreground flex justify-between text-sm">
                <span>Lower</span>
                <span>Higher</span>
              </div>
            </div>
          </>
        ) : (
          <>
            {/* Speed (mistv2 only) */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label className="text-foreground text-sm font-medium">Speed</Label>
                <span className="text-foreground text-sm font-bold">
                  {currentModelSettings.speed?.toFixed(1)}
                </span>
              </div>
              <Slider
                value={[currentModelSettings.speed || DEFAULT_MISTV2_SETTINGS.speed]}
                onValueChange={(value) => updateModelSettings({ speed: value[0] })}
                max={2}
                min={0.5}
                step={0.1}
                className="w-full"
              />
              <div className="text-muted-foreground flex justify-between text-sm">
                <span>Slower</span>
                <span>Faster</span>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
