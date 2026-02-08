import { ChevronDown, Sparkles, Zap, Lightbulb, BrainCircuit } from "lucide-react";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";

export type ModelType = "auto" | "gemini-2.5-flash" | "gemini-2.5-flash-lite" | "sonar-pro";

interface ModelSelectorProps {
    selectedModel: ModelType;
    onSelect: (model: ModelType) => void;
    isLoading?: boolean;
}

const ModelSelector = ({ selectedModel, onSelect, isLoading }: ModelSelectorProps) => {

    const getModelLabel = (model: ModelType) => {
        switch (model) {
            case "auto": return "AI Career Pilot v2 (Auto)";
            case "gemini-2.5-flash": return "Gemini 2.5 Flash";
            case "gemini-2.5-flash-lite": return "Gemini 2.5 Flash-Lite";
            case "sonar-pro": return "Perplexity Sonar-Pro";
            default: return "AI Career Pilot v2";
        }
    };

    const getModelIcon = (model: ModelType) => {
        switch (model) {
            case "auto": return <Sparkles className="h-3 w-3 text-indigo-500" />;
            case "gemini-2.5-flash": return <Zap className="h-3 w-3 text-amber-500" />;
            case "gemini-2.5-flash-lite": return <Lightbulb className="h-3 w-3 text-green-500" />;
            case "sonar-pro": return <BrainCircuit className="h-3 w-3 text-blue-500" />;
            default: return <Sparkles className="h-3 w-3" />;
        }
    };

    return (
        <DropdownMenu>
            <DropdownMenuTrigger disabled={isLoading} asChild>
                <button
                    className={cn(
                        "flex items-center gap-1.5 px-3 py-1 rounded-full",
                        "bg-muted/50 border border-border/50 hover:bg-muted hover:border-border",
                        "text-[11px] font-medium text-muted-foreground transition-all",
                        isLoading && "opacity-50 cursor-not-allowed"
                    )}
                >
                    {getModelIcon(selectedModel)}
                    <span className="truncate max-w-[120px]">{getModelLabel(selectedModel)}</span>
                    <ChevronDown className="h-3 w-3 opacity-50" />
                </button>
            </DropdownMenuTrigger>

            <DropdownMenuContent align="start" className="w-[220px]">
                <DropdownMenuLabel className="text-xs text-muted-foreground font-normal uppercase tracking-wider">
                    Reasoning Model
                </DropdownMenuLabel>

                <DropdownMenuItem onClick={() => onSelect("auto")} className="flex items-center justify-between cursor-pointer">
                    <div className="flex items-center gap-2">
                        <Sparkles className="h-4 w-4 text-indigo-500" />
                        <div className="flex flex-col">
                            <span className="font-medium">Auto (Smart)</span>
                            <span className="text-[10px] text-muted-foreground">Best model for the task</span>
                        </div>
                    </div>
                    {selectedModel === "auto" && <div className="h-1.5 w-1.5 rounded-full bg-indigo-500" />}
                </DropdownMenuItem>

                <DropdownMenuSeparator />

                <DropdownMenuItem onClick={() => onSelect("gemini-2.5-flash")} className="flex items-center justify-between cursor-pointer">
                    <div className="flex items-center gap-2">
                        <Zap className="h-4 w-4 text-amber-500" />
                        <div className="flex flex-col">
                            <span className="font-medium">Gemini 2.5 Flash</span>
                            <span className="text-[10px] text-muted-foreground">Fast & Intelligent</span>
                        </div>
                    </div>
                    {selectedModel === "gemini-2.5-flash" && <div className="h-1.5 w-1.5 rounded-full bg-amber-500" />}
                </DropdownMenuItem>

                <DropdownMenuItem onClick={() => onSelect("gemini-2.5-flash-lite")} className="flex items-center justify-between cursor-pointer">
                    <div className="flex items-center gap-2">
                        <Lightbulb className="h-4 w-4 text-green-500" />
                        <div className="flex flex-col">
                            <span className="font-medium">Flash-Lite</span>
                            <span className="text-[10px] text-muted-foreground">Speed optimized</span>
                        </div>
                    </div>
                    {selectedModel === "gemini-2.5-flash-lite" && <div className="h-1.5 w-1.5 rounded-full bg-green-500" />}
                </DropdownMenuItem>

                <DropdownMenuSeparator />

                <DropdownMenuItem onClick={() => onSelect("sonar-pro")} className="flex items-center justify-between cursor-pointer">
                    <div className="flex items-center gap-2">
                        <BrainCircuit className="h-4 w-4 text-blue-500" />
                        <div className="flex flex-col">
                            <span className="font-medium">Sonar-Pro</span>
                            <span className="text-[10px] text-muted-foreground">Deep Internet Search</span>
                        </div>
                    </div>
                    {selectedModel === "sonar-pro" && <div className="h-1.5 w-1.5 rounded-full bg-blue-500" />}
                </DropdownMenuItem>

            </DropdownMenuContent>
        </DropdownMenu>
    );
};

export default ModelSelector;
