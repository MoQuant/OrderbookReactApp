import React from 'react';
import Plot from 'react-plotly.js';

export default class App extends React.Component {

  constructor(){
    super();

    this.state = {
      response: null
    }

    this.plotBooks = this.plotBooks.bind(this)
  }

  componentDidMount() {
    const socket = new WebSocket('ws://localhost:8080')

    socket.onmessage = (evt) => {
      this.setState({ response: JSON.parse(evt.data)})
    }

  }

  plotBooks() {
    const graphs = []
    const {response} = this.state
    if(response !== null){
      Object.keys(response).map((tick, i) => {
        graphs.push(
          <Plot 
            data={[{
              x: response[tick]['bid_x'],
              y: response[tick]['bid_y'],
              type: 'bar',
              marker: {
                color: 'red'
              },
              name: "Bids"
            },{
              x: response[tick]['ask_x'],
              y: response[tick]['ask_y'],
              type: 'bar',
              marker: {
                color: 'limegreen'
              },
              name: "Asks"
            }]}
            layout={{
              title: tick + " Orderbook",
              width: 300,
              height: 300
            }}
          />
        )
      })
    }
    return graphs
  }

  render() {
    return (
      <React.Fragment>
        <center>{this.plotBooks()}</center>
      </React.Fragment>
    );
  }
}