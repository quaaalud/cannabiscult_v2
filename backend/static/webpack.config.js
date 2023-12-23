const path = require('path');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const TerserPlugin = require("terser-webpack-plugin");
const webpack = require('webpack');
const globAll = require('glob-all'); // Import glob-all

module.exports = {
  entry: {
    // Use glob-all to collect all .js files recursively starting from the root
    main: globAll.sync([
      './**/*.js', // Match .js files
      '!./node_modules/**', // Exclude node_modules directory
    ], {
      absolute: true, // Convert paths to absolute
      deep: 5, // Collect files up to 5 directories deep
    }),
  },
  output: {
    path: path.resolve(__dirname, 'static/dist'),
    filename: '[name].[contenthash].bundle.js'
  },
  optimization: {
    innerGraph: true,
    flagIncludedChunks: true,
    concatenateModules: true,
    minimize: true,
    minimizer: [
      new TerserPlugin({
        test: /\.js(\?.*)?$/i,
      }),
    ],
    splitChunks: {
      chunks: 'all',
    },
    runtimeChunk: 'single',
  },
  plugins: [
    new webpack.ProvidePlugin({
      Chart: 'chart.js',
    }),
    new MiniCssExtractPlugin({
      filename: '[name].[contenthash].css',
    }),
  ],
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env']
          }
        }
      },
      {
        test: /\.(s[ac]ss|css)$/,
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: 'css-loader',
            options: {
              sourceMap: true,
            },
          },
          {
            loader: 'sass-loader',
            options: {
              sourceMap: true,
            },
          },
        ],
      },
    ],
  },
  resolve: {
    alias: {
      'duplicate-library': 'path/to/existing/library',
    },
  },
  devtool: 'source-map',
};
