import Graph from 'vis-react';
import {useState, useEffect} from 'react';

function FilmGraph() {

    var graph = {};

    const options = {
        height: "100%",
        width: "100%",
        improvedLayout: false,
        layout: {
            hierarchical: false,
        },
        edges: {
            width: 3,
            color: "#fff",
            arrowStrikethrough: false,
        },
        physics: {
            enabled: false,
            solver: "repulsion",
            repulsion: {
                nodeDistance: 600,
            },
            stabilization: {
                enabled: true,
                iterations: 200,
                updateInterval: 10,
                onlyDynamicEdges: false,
                fit: true
            }
        },
        nodes: {
            fixed: false
        },
        groups: {
            films: {
                size: 110,
                shape: "image",
                font: {
                    size: 0
                }
            },
            actors: {
                size: 75,
                shape: "circularImage",
                borderWidth: 5,
                color: "white",
                font: {
                    face: "Bahnschrift",
                    color: "black",
                    background: "white",
                    size: 20,
                    vadjust: -20
                },
                selected: {
                    font: {
                        face: "arial"
                    }
                }
            }
        },
        interaction: {
            hoverEdges: false,
            hover: true,
        }
    };

    return (
        <div>
            <Graph graph={graph} options={options}/>
        </div>
    )
};

export default FilmGraph;