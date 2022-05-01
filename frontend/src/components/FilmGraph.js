// import Graph from 'vis-react';
import React from 'react';

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
}

class FilmGraph extends React.Component {
    constructor(props) {
        super(props)
        var url = 'http://127.0.0.1:8000/api/';
        switch(props.mode) {
            case 'graph':
                url = url + 'graph?root=' + props.root.replace(' ', '%20') + '&depth=' + props.depth;
                break;
            case 'path': 
                url = url + 'path?left=' + props.left.replace(' ', '%20') + '&right=' + props.right.replace(' ', '%20');
                break;
            default:
                break;
        }
        this.state = {
            url: url,
            graph: {nodes: [], edges: []}
        }
    }

    componentDidMount() {
        // try {
        //     console.log(this.state.url)
        //     fetch(this.state.url)
        //         .then(response => {
        //             if (response.ok) {
        //                 return response.json()
        //             } else {
        //                 throw new Error ('Backend query failed')
        //             }
        //         })
        //         .then(json => this.setState({graph: json}));
        // } catch(error) {
        //     console.log(error)
        // }
    }

    render() {
        console.log(this.state.graph)
        try {
            // return(<Graph/>)
        }
        catch(error) {
            console.log(error)
        }
            // return(<Graph data={this.state.graph} options={options} events={{}}/>)
        return (<></>)
    }
}

export default FilmGraph;