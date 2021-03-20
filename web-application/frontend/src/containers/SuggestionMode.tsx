import React, { useCallback, useEffect, useState } from 'react'
//@ts-ignore
import { Container, Row, Col, Button } from '@bootstrap-styled/v4';
import axios from 'axios';
import Suggestion from '../components/Suggestion';
import styled from 'styled-components';
//@ts-ignore
import { Ring } from "react-awesome-spinners";


export default function SuggestionMode({ itemName, onDone, onOutOfItems }:
    {
        itemName: string,
        onDone: (iterationsNeeded: number, startItems: string[], targetItem: string, history: string[]) => void,
        onOutOfItems: () => void
    }) {
    const [suggestions, setSuggestions] = useState<string[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [imageLoading, setImageLoading] = useState<boolean>(true);
    const [currentItem, setCurrentItem] = useState<string>("");
    const [showPlot, setShowPlot] = useState<boolean>(false);

    const backendUrl = process.env.REACT_APP_BACKEND_URL || `http://localhost:5050`;

    const item = itemName || "item";

    const getSuggestions = useCallback(
        (item: string) => {
            const url = `${backendUrl}/suggestions${item ? `?item=${item}` : ""}`;
            setLoading(true);
            axios
                .get<{ items: string[] }>(url, { withCredentials: true })
                .then(res => {
                    setLoading(false);
                    setSuggestions(res.data.items);
                    if(res.data.items.length <= 0) onOutOfItems();
                })
                .catch(err => {
                    if (err.response) {
                        console.error(`error: ${err.response.data}`);
                    } else {
                        console.log(err.message);
                    }
                })
        }, [backendUrl, onOutOfItems])

    // inital suggestions
    useEffect(() => {
        getSuggestions("");
    }, [backendUrl, getSuggestions])

    const showMoreItems = () => {
        getSuggestions(currentItem);
    }

    const onSuggestionSelect = (item: string) => {
        setShowPlot(false)
        setCurrentItem(item);
        getSuggestions(item);
    }

    const undo = () => {
        const undoUrl = `${backendUrl}/undo`;
        setShowPlot(false);
        setLoading(true);
        axios
            .get<{ currentItem: string, items: string[] }>(undoUrl, { withCredentials: true })
            .then(res => {
                setLoading(false);
                setCurrentItem(res.data.currentItem)
                setSuggestions(res.data.items);
            })
            .catch(err => {
                if (err.response) {
                    console.error(`error: ${err.response.data}`);
                } else {
                    console.log(err.message);
                }
            })
    }

    const done = () => {
        const doneUrl = `${backendUrl}/done${currentItem ? `?item=${currentItem}` : ""}`;
        setLoading(true);
        axios
            .get<{ start_items: string[], iterations: number, sequence: string[] }>(doneUrl, { withCredentials: true })
            .then(res => {
                setLoading(false);
                onDone(res.data.iterations, res.data.start_items, currentItem, res.data.sequence);
            })
            .catch(err => {
                if (err.response) {
                    console.error(`error: ${err.response.data}`);
                } else {
                    console.log(err.message);
                }
            })
    }

    useEffect(() => {
        if (loading) setShowPlot(false)
        setImageLoading(true)
    }, [loading])

    return <Container
        className='pt-5'>
        {loading ?
            <Row
                className='d-flex justify-content-center'>
                <Ring />
            </Row>
            :

            <>
                <Row
                    className='d-flex justify-content-center'>
                    Which one of these {item}s is closest to your {item}{currentItem && `, and closer than "${currentItem.replaceAll("_", " ")}"`}?
        </Row>
                <Row
                    className='mb-3 d-flex justify-content-center align-items-center'>
                    {suggestions.map((suggestion, index) =>
                        <Col
                            key={`suggestion_${index}`}
                            xs="4"
                            md="3"
                            className='mt-3'>
                            <Suggestion
                                item={suggestion}
                                onClick={() => onSuggestionSelect(suggestion)} />
                        </Col>
                    )}
                </Row>
            </>}
        <Row
            className='d-flex justify-content-center'>
            {loading
                || !currentItem
                || <Button
                    className='m-1 btn-danger' onClick={showMoreItems}>
                    ↻ None of the above, show more {item}s
        </Button>}
            {loading
                || !currentItem
                || <StyledButton
                    onClick={() => done()}
                    className='m-1 btn-success'>
                    👍 "{currentItem.replaceAll("_", " ")}" is what I was thinking of
          </StyledButton>}
            {loading
                || !currentItem
                || <StyledButton
                    onClick={() => undo()}
                    className='m-1 btn-secondary'>
                    ⬅ Undo
          </StyledButton>}
            {loading
                || <Button
                    onClick={() => setShowPlot(!showPlot)}
                    className='m-1 btn-secondary'>
                    {showPlot ? `Hide` : `Show`} {item}s in 2D space
          </Button>}
        </Row>
        <Row className='d-flex justify-content-center'>
            {showPlot &&
                <>
                    {imageLoading && <Ring />}
                    <img
                        // avoid caching with Date.now()
                        key={Date.now()}
                        alt="Plotted items"
                        src={`${backendUrl}/plot?time=${Date.now()}`}
                        className="img-fluid"
                        onLoad={() => setImageLoading(false)}
                        style={{ width: `100%` }}
                    />
                </>}
        </Row>
    </Container>
}


const StyledButton = styled(Button)`
//width: 100%;
white-space:normal !important;
word-wrap: break-word; 
`