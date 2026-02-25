import * as React from 'react';
import type { ShowWave, WaveComponent } from './interface';
declare const useWave: (nodeRef: React.RefObject<HTMLElement | null>, className: string, component?: WaveComponent) => ShowWave;
export default useWave;
