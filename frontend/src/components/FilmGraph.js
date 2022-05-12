import Graph from 'vis-react';
import React from 'react';

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
            color: "rgba(0,0,0,0.4)",
            hover: "rgba(0,0,0,0.6)",
            highlight: "rgba(0,0,0,0.8)",
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
            font: {
                size: 30,
                face: 'Bahnschrift',
                strokeWidth: 6
            }
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
                strokeWidth: 3,
                vadjust: '-20'
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
        this._network = React.createRef()
        this.state = {
            uri: props.uri,
            nodes: [],
            edges: [],
            events: props.events
        }
    }

    componentDidMount() {
        console.log(this.state.uri)
        fetch(this.state.uri)
            .then(response => response.json())
            .then(json => this.setState({
                nodes: json.nodes,
                edges: json.edges
            }))
            .catch((error) => console.log(error))
    }

    render() {
        // vis.js only supports displaying static graphs.
        // To display the data stored in this instance's state,
        // a random key is used to make a distinct deep copy.
        const key = Math.random()
        return(
            <Graph
                ref={this._network}
                key={key}
                graph={{
                    nodes: this.state.nodes.map(n => Object.assign(n, {network: key})),
                    edges: this.state.edges.map(e => Object.assign(e, {network: key})),
                }}
                options={options}
                events={this.state.events}
            />
        )
    }
}

export default FilmGraph;