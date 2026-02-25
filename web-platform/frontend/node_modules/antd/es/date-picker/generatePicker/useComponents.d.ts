import type { Components } from 'rc-picker/lib/interface';
export default function useComponents(components?: Components): {
    time?: import("react").ComponentType<import("rc-picker/lib/interface").SharedPanelProps<any>> | undefined;
    date?: import("react").ComponentType<import("rc-picker/lib/interface").SharedPanelProps<any>> | undefined;
    week?: import("react").ComponentType<import("rc-picker/lib/interface").SharedPanelProps<any>> | undefined;
    month?: import("react").ComponentType<import("rc-picker/lib/interface").SharedPanelProps<any>> | undefined;
    quarter?: import("react").ComponentType<import("rc-picker/lib/interface").SharedPanelProps<any>> | undefined;
    year?: import("react").ComponentType<import("rc-picker/lib/interface").SharedPanelProps<any>> | undefined;
    decade?: import("react").ComponentType<import("rc-picker/lib/interface").SharedPanelProps<any>> | undefined;
    datetime?: import("react").ComponentType<import("rc-picker/lib/interface").SharedPanelProps<any>> | undefined;
    button: string | import("react").ComponentClass<any, any> | import("react").FC<Readonly<import("../..").ButtonProps>>;
    input?: React.ComponentType<any> | string;
};
