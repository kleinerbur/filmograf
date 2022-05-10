import { Button } from '@mui/material';
import ButtonGroup from '@mui/material/ButtonGroup';
import React from 'react';
// import './Form.css';

// base: 52af77
// bg: 4da570
// font: 1f4637

const selectedSx = {
    fontFace: 'Bahnschrift',
    fontWeight: 'bold',
    backgroundColor: '#63b784',
    color: 'white',
    fontSize: 15,
    border: '0px solid white',
    ':hover': {
        border: '0px solid white',
        backgroundColor: 'white',
        color: '#1f4637',
    },
    ':disabled': {
        color: 'white'
    }
};

const unselectedSx = {
    fontFace: 'Bahnschrift',
    fontWeight: 'bold',
    backgroundColor: '#4da570',
    color: '#1f4637',
    fontSize: 15,
    border: '0px solid white',
    ':hover': {
        border: '0px solid white',
        backgroundColor: 'white',
        color: '#1f4637'
    },
};

class Menu extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            onClick:       props.onClick,
            modeGraph:     props.modeGraph,
            pathButtonSx:  props.modeGraph ? unselectedSx : selectedSx,
            graphButtonSx: props.modeGraph ? selectedSx : unselectedSx
        }
        this._pathButton  = React.createRef()
        this._graphButton = React.createRef()
    }

    graphMode = () => this.setState({
            modeGraph:     true,
            pathButtonSx:  unselectedSx,
            graphButtonSx: selectedSx  
        })
    
    pathMode = () => this.setState({
        modeGraph:     false,
        pathButtonSx:  selectedSx,
        graphButtonSx: unselectedSx  
    })

    render() {
        return (
            <ButtonGroup 
                className='modeButtons'
                variant='outlined'
                orientation='vertical'
                sx={{border: '2px solid #4da570'}}>
                <Button
                    ref={this._pathButton}
                    id='pathButton'
                    sx={this.state.pathButtonSx}
                    disabled={!this.state.modeGraph}
                    onClick={this.state.onClick}>
                        Út
                </Button>
                <Button
                    ref={this._graphButton}
                    id='graphButton'
                    sx={this.state.graphButtonSx}
                    disabled={this.state.modeGraph}
                    onClick={this.state.onClick}>
                        Gráf
                </Button>
            </ButtonGroup>
        )
    }
}

export default Menu;