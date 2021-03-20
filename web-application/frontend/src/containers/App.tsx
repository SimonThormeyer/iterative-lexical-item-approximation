//@ts-ignore
import BootstrapProvider from '@bootstrap-styled/provider/lib/BootstrapProvider';
import { useState } from 'react';
import ModelSelection from './ModelSelection';
import SuggestionMode from './SuggestionMode';
import Done from './Done';

enum Mode {
    ChooseModel,
    Suggestions,
    Done
}

export default function App() {
    const [mode, setMode] = useState<Mode>(Mode.ChooseModel);
    const [itemName, setItemName] = useState<string>("");
    const [{ iterations, startItems, history, targetItem }, setDoneProps] =
        useState<{
            iterations: number;
            startItems: string[];
            targetItem: string;
            history: string[];
        }>
            ({
                iterations: 0, startItems: [], targetItem: "", history: []
            });

    return <BootstrapProvider>
        {mode === Mode.ChooseModel
            && <ModelSelection onSelectModel={itemName => {
                setItemName(itemName)
                setMode(Mode.Suggestions)
            }} />}
        {mode === Mode.Suggestions
            && <SuggestionMode
                itemName={itemName}
                onOutOfItems={() => setMode(Mode.ChooseModel)}
                onDone={(iterations, startItems, targetItem, history) => {
                    setMode(Mode.Done);
                    setDoneProps({
                        iterations: iterations,
                        startItems: startItems,
                        targetItem: targetItem,
                        history: history
                    });
                }} />}
        {mode === Mode.Done
            && <Done
                target={targetItem}
                iterations={iterations}
                startItems={startItems}
                history={history} />}
    </BootstrapProvider>;

}