import React from 'react';
type RenderFunction<T extends any[]> = (...args: T) => React.ReactNode;
declare function usePopupRender<T extends [React.ReactElement, ...any[]]>(renderFn?: RenderFunction<T>): ((...args: T) => React.ReactElement) | undefined;
export default usePopupRender;
