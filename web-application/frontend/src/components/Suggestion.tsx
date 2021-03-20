import React from 'react'
//@ts-ignore
import { Button} from '@bootstrap-styled/v4';
import styled from 'styled-components';

const StyledButton = styled(Button)`
width: 100%;
white-space:normal !important;
word-wrap: break-word; 
`

export default function Suggestion({ item, onClick }: { item: string; onClick: () => void; }) {
    return <StyledButton onClick={onClick}>{item.replaceAll("_", " ")}</StyledButton>;
}