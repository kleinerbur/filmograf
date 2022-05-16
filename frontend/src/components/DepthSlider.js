import Slider from '@mui/material/Slider';
import React from 'react';

class DepthSlider extends React.Component {
    constructor(props){
        super(props)
        this.state = {
            max:      props.max,
            value:    props.value,
            onChange: props.onChange,
            hidden:   props.hidden,
            name:     props.name
        }
    }

    hide   = () => this.setState({hidden: true})
    unhide = () => this.setState({hidden: false})
    
    render() {
        if (this.state.hidden) return (<></>)
        return (<Slider
                    hidden={this.state.hidden}
                    name={this.state.name}
                    id={this.state.name}
                    valueLabelDisplay='on'
                    min={0} 
                    max={this.state.max}
                    step={0.5}
                    marks
                    defaultValue={this.state.value}
                    onChange={this.state.onChange}/>)
    }
}

export default DepthSlider;