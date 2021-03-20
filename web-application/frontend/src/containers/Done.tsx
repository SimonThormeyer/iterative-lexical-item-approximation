//@ts-ignore
import { Container, Row, H1, Button } from '@bootstrap-styled/v4';
import axios from 'axios';
import { useState } from 'react';
//@ts-ignore
import { Ring } from "react-awesome-spinners";

export default function Done({ target, iterations, startItems, history }: { target: string; iterations: number; startItems: string[]; history: string[]; }) {
    const [imageLoading, setImageLoading] = useState<boolean>(true);
    const [saving, setSaving] = useState(false);
    const [saved, setSaved] = useState(false);
    const backendUrl = process.env.REACT_APP_BACKEND_URL || `http://localhost:5050`;

    const saveResults = () => {
        setSaving(true);
        const url = `${backendUrl}/save-results`;
        axios
            .get<string>(url, { withCredentials: true })
            .then(res => {
                console.log(`saving finished, response: ${res.data}`);
                setSaved(true);
            })
            .catch(err => {
                if (err.response) {
                    console.error(`error: ${err.response.data}`);
                } else {
                    console.log(err.message);
                }
            });
    }

    return <Container className='pt-1'>
        <Row>
            <H1>
                Finished!
            </H1>
        </Row>
        <Row>
            Target: {target.replaceAll("_", " ")}
        </Row>
        <Row>
            Iterations needed: {iterations}
        </Row>
        <Row>
            <span
                style={{ marginRight: '.3rem' }}>
                Selection history:
                </span>
            {history.map((item, index) =>
                <span
                    style={{ marginRight: '.3rem' }}
                    key={`history_${index}`}>
                    {` ${item.replaceAll("_", " ")}${index !== history.length - 1 ? "," : ""}`}
                </span>)}
        </Row>
        {target
            && <>
                <Row className='d-flex justify-content-center'>
                    {imageLoading
                        && <Ring />}
                    <img
                        // avoid caching with Date.now()
                        key={Date.now()}
                        alt="Plotted items"
                        src={`${backendUrl}/result-plot?item=${target}`}
                        className="img-fluid"
                        onLoad={() => setImageLoading(false)}
                        style={{ maxWidth: `100%`, maxHeight: '100%' }}
                    />
                </Row>
                {saving
                    || saved
                    || <Row className='mt-3 d-flex justify-content-center'>
                        <Button
                            onClick={saveResults}
                        >
                            Save results on server
            </Button>
                    </Row>}
                {saving
                    && (saved
                        || <Row className='mt-3 d-flex justify-content-center'>
                            <Ring />
                        </Row>)}
            </>}
    </Container>;
}

