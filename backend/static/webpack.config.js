const path = require('path');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const TerserPlugin = require("terser-webpack-plugin");
const webpack = require('webpack');

module.exports = {
  entry: {
    main: './js/mdb.min.js',
    styles: './css/styles.css'
  },
  output: {
    path: path.resolve(__dirname, 'static/dist'),
    filename: '[name].bundle.js'
  },
  optimization: {
    innerGraph: true,
    flagIncludedChunks: true,
    concatenateModules: true,
    minimize: true,
    minimizer: [
      new TerserPlugin({ test: /\.js(\?.*)?$/i }),
      new CssMinimizerPlugin() // Added for CSS minimization
    ],
  },
  plugins: [
    new webpack.ProvidePlugin({
      Chart: 'chart.js',
    }),
    new MiniCssExtractPlugin()
  ],
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [MiniCssExtractPlugin.loader, 'css-loader'] // Removed 'style-loader' and 'sass-loader' for '.css' files
      },
      {
        test: /\.scss$/,
        use: [MiniCssExtractPlugin.loader, 'css-loader', 'sass-loader'] // Separate rule for '.scss' files if needed
      },
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env']
          }
        }
      }
    ],
  },
  devtool: 'inline-source-map',
  devServer: {
    contentBase: './static/dist',
  },
  resolve: {
    extensions: ['.js', '.jsx', '.json', '.css', '.scss'],
  }
};
