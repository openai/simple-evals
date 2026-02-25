import { QrCode } from '../libs/qrcodegen';
import type { ErrorCorrectionLevel, ImageSettings } from '../interface';
interface Options {
    value: string | string[];
    level: ErrorCorrectionLevel;
    minVersion: number;
    includeMargin: boolean;
    marginSize?: number;
    imageSettings?: ImageSettings;
    size: number;
    boostLevel?: boolean;
}
export declare const useQRCode: (opt: Options) => {
    cells: boolean[][];
    margin: number;
    numCells: number;
    calculatedImageSettings: {
        x: number;
        y: number;
        h: number;
        w: number;
        excavation: import("../interface").Excavation;
        opacity: number;
        crossOrigin: import("../interface").CrossOrigin;
    };
    qrcode: QrCode;
};
export {};
