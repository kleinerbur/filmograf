import Graph from 'vis-react';
import React from 'react';
import Network from 'vis-react';

const options = {
    layout: {
        improvedLayout: true,
        hierarchical: false,
    },
    nodes: {
        fixed: false
    },
    edges: {
        width: 2,
        color: {
            color: "#555",
            hover: "#333",
            highlight: "#111",
            opacity: 0.4
        },
        font: {
            face: 'Bahnschrift',
            background: 'white',
            strokeWidth: 0,
            size: 8,
            color: '#444',
            align: 'middle'
        },
        arrows: {
            to: {
                enabled: false
            }
        }
    },
    physics: {
        enabled: true,
        barnesHut: {
            springConstant: 0,
            avoidOverlap: 10
        },
        stabilization: {
            enabled: true,
            iterations: 200,
            updateInterval: 10,
            onlyDynamicEdges: false,
            fit: true
        }
    },
    groups: {
        films: {
            size: 60,
            shape: "image",
            font: {size: 20}
        },
        actors: {
            size: 30,
            borderWidth: 0,
            shape: "circularImage",
            color: {
                background: "#4da570",
                hover: "#1f4637",
                highlight: "#367654"
            },
            font: {
                size: 20,
                face: "Bahnschrift",
                color: "#1f4637",
                strokeWidth: 3
            }
        }
    },
    interaction: {
        hoverEdges: false,
        hover: true
    }
}

class FilmGraph extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            width: props.width.toString(),
            height: "830",
            uri: props.uri,
            nodes: [],
            edges: []
        }
    }

    componentDidMount() {
        try {
            console.log(this.state.uri)
            fetch(this.state.uri)
                .then(response => {
                    if (response.ok) {
                        return response.json()
                    } else {
                        throw new Error ('Backend query failed')
                    }
                })
                .then(json => this.setState({
                    nodes: json.graph.nodes,
                    edges: json.graph.edges
                }));
        } catch(error) {
            console.log(error)
        }
    }

    render() {
        const key = Math.random()
        var _network = React.createRef()
        try {
            return(
                <Graph
                    ref={_network}
                    key={key}
                    graph={{
                        nodes: this.state.nodes.map(n => Object.assign(n, {network: key})),
                        edges: this.state.edges.map(e => Object.assign(e, {network: key})),
                    }}
                    options={{
                        ...options,
                        width: this.state.width,
                        height: this.state.height
                    }}
                />
            )
        }
        catch(error) {
            console.log(error)
        }
        return (<></>)
    }
}

export default FilmGraph;