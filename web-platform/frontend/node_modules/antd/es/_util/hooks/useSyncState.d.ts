type UseSyncStateProps<T> = readonly [() => T, (newValue: T) => void];
export declare const useSyncState: <T>(initialValue: T) => UseSyncStateProps<T>;
export {};
