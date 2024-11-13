# Sample GenLayer project
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/license/mit/)
[![Discord](https://dcbadge.vercel.app/api/server/8Jm4v89VAu?compact=true&style=flat)](https://discord.gg/8Jm4v89VAu)
[![Telegram](https://img.shields.io/badge/Telegram--T.svg?style=social&logo=telegram)](https://t.me/genlayer)
[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/yeagerai.svg?style=social&label=Follow%20%40GenLayer)](https://x.com/GenLayer)
[![GitHub star chart](https://img.shields.io/github/stars/yeagerai/genlayer-project-boilerplate?style=social)](https://star-history.com/#yeagerai/genlayer-js)

## 👀 About
This project includes a sample implementation of an Adaptive Automated Market Maker (AMM) using GenLayer. The project demonstrates two different approaches to market making:

1. A basic AMM with simulated fixed values
2. An advanced AMM that simulates real market behavior using CCXT (currently in development)

## 📦 What's included
- Basic requirements to deploy and test your intelligent contracts locally
- Configuration file template
- Test functions to write complete end-to-end tests
- Two implementations of an Adaptive AMM contract
- Example end-to-end tests for the contracts provided
- Vue.js frontend to interact with the contracts

## 🛠️ Requirements
- A running GenLayer simulator (Install from [GenLayer Simulator](https://github.com/yeagerai/genlayer-simulator)). This repository code does not need to be located in the same directory as the Genlayer Simulator.

## 🚀 Steps to run this example

### 1. Configure environment
   Rename the `.env.example` file to `.env`, then fill in the values for your configuration.

### 2. Deploy the contract
   Deploy either the basic AMM contract from `/contracts/amm_adaptative.py` or the simulated version from `/contracts/amm_adaptative_simulated.py` using the Simulator's UI:
   1. Open the GenLayer Simulator interface in your web browser (usually at http://localhost:8080).
   2. Create a new file in the "Contracts" section and paste the content of your chosen contract.
   3. Navigate to the "Run and Debug" section.
   4. Follow the on-screen instructions to complete the deployment process.

### 3. Setup the frontend environment
  1. All the content of the dApp is located in the `/app` folder.
  2. Rename the `.env.example` file in the `/app` folder to `.env`.
  3. Add the deployed contract address to the `/app/.env` under the variable `VITE_CONTRACT_ADDRESS`

### 4. Run the frontend Vue app
   Ensure your GenLayer Simulator is running, and execute the following commands in your terminal:
   ```shell
   cd app
   npm install
   npm run dev
   ```
   The terminal should display a link to access your frontend app (usually at http://localhost:5173/).
   For more information on the code see [GenLayerJS](https://github.com/yeagerai/genlayer-js).

## 🤖 How the Adaptive AMM Contracts Work

The project includes two different implementations of an Adaptive AMM:

### Basic AMM (`amm_adaptative.py`)
This contract provides a basic implementation with fixed simulated values. It's useful for testing and development purposes. Features include:
- Simulated order book data
- Fixed current price and volume
- Predefined open orders and balances
- Basic market making logic using LLM

### Advanced Simulated AMM (`amm_adaptative_simulated.py`)
This contract provides a more realistic market making simulation using CCXT. Features include:
- Real-time market data simulation
- Dynamic order book management
- Realistic price and volume simulation
- Advanced market making strategies
- Balance and order constraints
- Volatility-based adjustments

Note: The advanced simulated version is currently under development due to encoding issues with CCXT integration.

## 🧪 Tests

This project includes integration tests that interact with the contracts deployed in the simulator. These tests cover the main functionalities of both AMM implementations:

1. Order book retrieval
2. Price and volume queries
3. Order management
4. Balance checks
5. Market making strategy execution

To run the tests, use:
```shell
pytest test
```

## 💬 Community
Connect with the GenLayer community to discuss, collaborate, and share insights:
- **[Discord Channel](https://discord.gg/8Jm4v89VAu)**: Our primary hub for discussions, support, and announcements.
- **[Telegram Group](https://t.me/genlayer)**: For more informal chats and quick updates.

Your continuous feedback drives better product development. Please engage with us regularly to test, discuss, and improve GenLayer.

## 📖 Documentation
For detailed information on how to use GenLayerJS SDK, please refer to our [documentation](https://docs.genlayer.io/).

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
