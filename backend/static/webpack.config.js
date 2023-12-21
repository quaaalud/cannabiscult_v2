const path = require('path');
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
  plugins: [
    new webpack.ProvidePlugin({
      Chart: 'chart.js',
    })
  ],
  module: {
    rules: [
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
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
};
