import axios from 'axios';
import { useEffect, useState } from 'react';
//@ts-ignore
import { Container, Row, Col, Button, H2, H1, P } from '@bootstrap-styled/v4';
//@ts-ignore
import { Ring } from "react-awesome-spinners";


type Model = {
    id: number;
    name: string;
    description: string;
    instructions: string;
    itemName: string;
    url?: string;
}

export default function ModelSelection({ onSelectModel }: {
    onSelectModel: (itemName: string) => void;
}) {
    const [loading, setLoading] = useState<boolean>(true);
    const [models, setModels] = useState<Model[]>([]);
    const [selectedModel, selectModel] = useState<number | null>(null);

    const backendUrl = process.env.REACT_APP_BACKEND_URL || `http://localhost:5050`;


    //get models initially
    useEffect(() => {
        setLoading(true);
        const url = `${backendUrl}/models`;
        axios
            .get<Model[]>(url, { withCredentials: true })
            .then(res => {
                setLoading(false);
                setModels(res.data);
            })
            .catch(err => {
                if (err.response) {
                    console.error(`error: ${err.response.data}`);
                } else {
                    console.log(err.message);
                }
            });

    }, [backendUrl]);

    // do http request to select model in backend
    useEffect(() => {
        if (selectedModel === null)
            return;
        setLoading(true);
        const url = `${backendUrl}/models?id=${selectedModel}`;
        axios
            .get<string>(url, { withCredentials: true })
            .then(res => {
                console.log(`request finished, response: ${res.data}`);
                onSelectModel(models[selectedModel].itemName);
            })
            .catch(err => {
                if (err.response) {
                    console.error(`error: ${err.response.data}`);
                } else {
                    console.log(err.message);
                }
            });
    }, [selectedModel, backendUrl, models, onSelectModel]);



    return <Container className='pt-1'>
        <H1>Iterative lexical item approximation</H1>
        <Row>
            <Col className='d-flex justify-content-center align-items-center' xs='12'>
                {loading && <Ring />}
                {models.length > 0 &&
                    <Container className='pt-3'>
                        <Row>
                            {models.map((model, i) => <Col xs='12' md='6' key={`model_${i}`}>
                                <Container className='pt-3'>
                                    <Row>
                                        <H2>Model {i + 1}</H2>
                                        <Col className='d-flex justify-content-center align-items-center' xs='12'>
                                            <Row>
                                                <P>
                                                    {model.instructions}
                                                </P>
                                                <P>
                                                    {model.description}
                                                </P>
                                            </Row>
                                        </Col>
                                        <Col className='d-flex justify-content-center align-items-center' xs='12'>
                                            <Button onClick={() => selectModel(i)} className='mt-3'>Select Model</Button>
                                        </Col>
                                    </Row>
                                </Container>
                            </Col>
                            )}
                        </Row>
                    </Container>}
            </Col>
        </Row>
    </Container>;
}