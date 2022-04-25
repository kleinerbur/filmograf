// import { useEffect } from 'react';
import Graph from 'vis-react';

import {useEffect, useState} from "react";

function FilmGraph() {

    let [graph, setGraph] = useState("");
    const url = "http://localhost:8000/api/graph?root=Emma%20Stone&depth=4";

    useEffect(() => {
        try {
            // setGraph("");
            fetch(url)
            .then(result => result.json())
            .then(json => {setGraph(json['graph']);})
        } catch (error) {
            console.log(error)
        }
    }, []);

    const options = {
        height: "100%",
        width: "100%",
        improvedLayout: false,
        layout: {
            hierarchical: false,
        },
        edges: {
            width: 5,
            color: "#fff",
            hoverWidth: 50,
            arrowStrikethrough: false,
        },
        physics: {
            barnesHut: {
              springConstant: 0,
              avoidOverlap: 2
            }
        },
        nodes: {
            color: "white",
            // opacity: 0.5,
            fixed: true,
            font: {
                face: 'Bahnschrift',
                size: 20,
                color: "black"
            },
            // shape: "circularImage",
            shape: "circle",
            widthConstraint: 20,
        },
        interaction: { hoverEdges: true }
    };

    return (
        <div>
            {/* <Graph graph={graph} options={options}/> */}
        </div>
    )    
};

export default FilmGraph;