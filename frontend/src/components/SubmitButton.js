import IconButton from '@mui/material/IconButton';
import DoubleArrowSharpIcon from '@mui/icons-material/DoubleArrowSharp';
import React from 'react';

class SubmitButton extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            onClick:  props.onClick,
            disabled: props.disabled
        }
    }

    disable = () => this.setState({disabled: true})
    enable  = () => this.setState({disabled: false})

    render() {
        return (<IconButton
                    variant='contained'
                    disabled={this.state.disabled}
                    onClick={this.state.onClick}>
                        <DoubleArrowSharpIcon/>
                        MEHET
                </IconButton>)
    }
}

export default SubmitButton;