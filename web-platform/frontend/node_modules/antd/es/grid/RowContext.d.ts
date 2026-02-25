export type GutterUnit = number | string;
export type RowContextGutter = readonly [GutterUnit, GutterUnit];
export interface RowContextState {
    gutter?: RowContextGutter;
    wrap?: boolean;
}
declare const RowContext: import("react").Context<RowContextState>;
export default RowContext;
