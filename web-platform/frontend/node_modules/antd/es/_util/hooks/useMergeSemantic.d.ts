import type { ValidChar } from '../type';
type TemplateSemanticClassNames<T extends string> = Partial<Record<T, string>>;
export type SemanticSchema = {
    _default?: string;
} & {
    [key: `${ValidChar}${string}`]: SemanticSchema;
};
export declare function mergeClassNames<T extends string, SemanticClassNames extends Partial<Record<T, any>> = TemplateSemanticClassNames<T>>(schema?: SemanticSchema, ...classNames: (SemanticClassNames | undefined)[]): any;
/**
 * Merge classNames and styles from multiple sources.
 * When `schema` is provided, it will **must** provide the nest object structure.
 */
export declare const useMergeSemantic: <ClassNamesType extends object, StylesType extends object>(classNamesList: (ClassNamesType | undefined)[], stylesList: (StylesType | undefined)[], schema?: SemanticSchema) => readonly [ClassNamesType, StylesType];
export {};
