export type PrevSelectedIndex = null | number;
/**
 * @title multipleSelect hooks
 * @description multipleSelect by hold down shift key
 */
export declare const useMultipleSelect: <T, K>(getKey: (item: T, index: number, array: T[]) => K) => readonly [(currentSelectedIndex: number, data: T[], selectedKeys: Set<K>) => K[], import("react").Dispatch<import("react").SetStateAction<PrevSelectedIndex>>];
