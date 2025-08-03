'use client';

import * as React from 'react';
import { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { cn } from '@/lib/utils';

type ModelType = 'arcana' | 'mist';
type VoiceType = 'prebuilt' | 'custom';

export function AISettingsPanel() {
  const [selectedModel, setSelectedModel] = useState<ModelType>('arcana');
  const [voiceType, setVoiceType] = useState<VoiceType>('prebuilt');
  const [selectedVoice, setSelectedVoice] = useState('luna');
  const [customVoiceDescription, setCustomVoiceDescription] = useState('');
  const [temperature, setTemperature] = useState([0.71]);
  const [repetitionPenalty, setRepetitionPenalty] = useState([1.5]);
  const [topP, setTopP] = useState([1.0]);

  const prebuiltVoices = [
    { value: 'luna', label: 'Luna' },
    { value: 'aria', label: 'Aria' },
    { value: 'nova', label: 'Nova' },
    { value: 'echo', label: 'Echo' },
  ];

  return (
    <div className="bg-background text-foreground h-full space-y-8 p-6">
      {/* Model Section */}
      <div className="space-y-4">
        <h2 className="text-foreground text-xl font-semibold">Model:</h2>
        <div className="flex flex-row gap-3">
          <Card
            className={cn(
              'hover:border-border flex-1 cursor-pointer border transition-all duration-200',
              selectedModel === 'arcana'
                ? 'border-neutral-500 bg-gradient-to-tr from-neutral-800 via-neutral-600 to-neutral-800 shadow-lg'
                : 'text-card-foreground border-border bg-gradient-to-tr from-black via-neutral-700 to-black hover:border-neutral-500 hover:bg-gradient-to-tl hover:from-neutral-800 hover:via-neutral-600 hover:to-neutral-800 hover:shadow-lg'
            )}
            onClick={() => setSelectedModel('arcana')}
          >
            <div className="p-4 text-center">
              <div className="mb-2 text-lg font-bold">ARCANA</div>
              <div className="text-sm opacity-80">Unmatched realism</div>
            </div>
          </Card>

          <Card
            className={cn(
              'hover:border-border flex-1 cursor-pointer border transition-all duration-200',
              selectedModel === 'mist'
                ? 'border-neutral-500 bg-gradient-to-tl from-neutral-800 via-neutral-600 to-neutral-800 shadow-lg'
                : 'text-card-foreground border-border bg-gradient-to-tl from-black via-neutral-700 to-black hover:border-neutral-500 hover:bg-gradient-to-tl hover:from-neutral-800 hover:via-neutral-600 hover:to-neutral-800 hover:shadow-lg'
            )}
            onClick={() => setSelectedModel('mist')}
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
        <h2 className="text-foreground text-xl font-semibold">Voice:</h2>

        <RadioGroup
          value={voiceType}
          onValueChange={(value) => setVoiceType(value as VoiceType)}
          className="space-y-4"
        >
          <div className="flex items-center space-x-3">
            <RadioGroupItem value="prebuilt" id="prebuilt" />
            <Label
              htmlFor="prebuilt"
              className="text-foreground cursor-pointer text-base font-medium"
            >
              Pre-built
            </Label>
          </div>

          {voiceType === 'prebuilt' && (
            <div className="ml-7 space-y-3">
              <Select value={selectedVoice} onValueChange={setSelectedVoice}>
                <SelectTrigger className="border-border bg-background text-foreground w-full">
                  <SelectValue />
                  <ChevronDown className="text-muted-foreground h-4 w-4" />
                </SelectTrigger>
                <SelectContent className="border-border bg-popover">
                  {prebuiltVoices.map((voice) => (
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
          )}

          <div className="flex items-center space-x-3">
            <RadioGroupItem value="custom" id="custom" />
            <Label
              htmlFor="custom"
              className="text-foreground cursor-pointer text-base font-medium"
            >
              Make your own <span className="text-muted-foreground">(beta)</span>
            </Label>
          </div>

          {voiceType === 'custom' && (
            <div className="ml-7">
              <textarea
                value={customVoiceDescription}
                onChange={(e) => setCustomVoiceDescription(e.target.value)}
                placeholder='Describe the voice, eg. "posh British woman" or "French chef from the countryside"'
                className="border-border bg-background text-foreground placeholder-muted-foreground focus:border-ring focus:ring-ring h-24 w-full resize-none rounded-lg border p-3 focus:ring-2 focus:outline-none"
              />
            </div>
          )}
        </RadioGroup>
      </div>

      {/* Settings Section */}
      <div className="space-y-6">
        <h2 className="text-foreground text-xl font-semibold">Settings:</h2>

        {/* Temperature */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label className="text-foreground text-base font-medium">Temperature</Label>
            <span className="text-foreground text-2xl font-bold">{temperature[0].toFixed(2)}</span>
          </div>
          <Slider
            value={temperature}
            onValueChange={setTemperature}
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
            <Label className="text-foreground text-base font-medium">Repetition Penalty</Label>
            <span className="text-foreground text-2xl font-bold">
              {repetitionPenalty[0].toFixed(1)}
            </span>
          </div>
          <Slider
            value={repetitionPenalty}
            onValueChange={setRepetitionPenalty}
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
            <Label className="text-foreground text-base font-medium">Top P</Label>
            <span className="text-foreground text-2xl font-bold">{topP[0].toFixed(0)}</span>
          </div>
          <Slider
            value={topP}
            onValueChange={setTopP}
            max={1}
            min={0}
            step={0.01}
            className="w-full"
          />
          <div className="text-muted-foreground flex justify-between text-sm">
            <span>Lower</span>
            <span>Higher</span>
          </div>
        </div>
      </div>
    </div>
  );
}
