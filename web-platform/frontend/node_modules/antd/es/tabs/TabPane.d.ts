import type * as React from 'react';
import type { TabPaneProps as RcTabPaneProps } from 'rc-tabs/lib/TabPanelList/TabPane';
import type { CompatibilityProps } from '.';
type TabPaneProps = CompatibilityProps & Omit<RcTabPaneProps, 'destroyInactiveTabPane'>;
declare const TabPane: React.FC<TabPaneProps>;
export type { TabPaneProps };
export default TabPane;
