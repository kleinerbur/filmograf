import IconButton from '@mui/material/IconButton';
import DoubleArrowSharpIcon from '@mui/icons-material/DoubleArrowSharp';
import React from 'react';

const defaultSx = {
    width: "130px",
    height: "50px",

    color: 'white',
    border: '2px solid white',
    borderRadius: 2,
    
    transition: '0.5s ease-in-out',

    ':hover': {
        border: '2px solid white',
        backgroundColor: 'white',
        color: '#1f4637'
    },

    ':disabled': {
        color: '#1f4637',
        backgroundColor: '#4da570',

        border: '0px solid white',
        borderRadius: 2,

        transition: '0.25s ease-in-out',
    }
};


class SubmitButton extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            onClick: props.onClick,
            disabled: props.disabled
        }
    }

    disable = () => this.setState({disabled: true})
    enable  = () => this.setState({disabled: false})

    render() {
        return (<IconButton
                    variant='contained'
                    disabled={this.state.disabled}
                    onClick={this.state.onClick}
                    sx={defaultSx}>
                        <DoubleArrowSharpIcon/>
                        MEHET
                </IconButton>
        )
    }
}

export default SubmitButton;