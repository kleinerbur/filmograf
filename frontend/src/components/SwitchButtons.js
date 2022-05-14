import { Button } from '@mui/material';
import ButtonGroup from '@mui/material/ButtonGroup';
import React from 'react';

class SwitchButtons extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            onClick:       props.onClick,
            modeGraph:     props.modeGraph,
        }
        this._pathButton  = React.createRef()
        this._graphButton = React.createRef()
    }

    graphMode = () => this.setState({modeGraph: true})
    pathMode  = () => this.setState({modeGraph: false})

    render() {
        return (
            <ButtonGroup 
                className='modeButtons'
                variant='outlined'
                orientation='vertical'
                sx={{border: '2px solid #4da570'}}>
                <Button
                    ref={this._pathButton}
                    id='path-button'
                    disabled={!this.state.modeGraph}
                    onClick={this.state.onClick}>
                        Út
                </Button>
                <Button
                    ref={this._graphButton}
                    id='graph-button'
                    disabled={this.state.modeGraph}
                    onClick={this.state.onClick}>
                        Gráf
                </Button>
            </ButtonGroup>
        )
    }
}

export default SwitchButtons;