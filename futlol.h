// Copyright 2019 DeepMind Technologies Ltd. All rights reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#ifndef OPEN_SPIEL_GAMES_FUTLOL_H_
#define OPEN_SPIEL_GAMES_FUTLOL_H_

#include <array>
#include <map>
#include <memory>
#include <string>
#include <vector>

#include "open_spiel/spiel.h"

// Parameters: none

namespace open_spiel {
namespace futlol {

// Constants.
inline constexpr int kNumPlayers = 6;
inline constexpr int kNumRows = 8;
inline constexpr int kNumCols = 8;
inline constexpr int kNumCells = kNumRows * kNumCols;
inline constexpr int kCellStates = 3 + 16; //kNumPlayers;  // empty, allied goal, enemy goal, players
const int moveSize = ceil(log2(kNumCells));
const int cellSize = ceil(log2(kCellStates));
inline constexpr int scoreTarget = 3;
inline constexpr int kMaxMoves = 2400;
inline constexpr double kMoveValue=0;
inline constexpr double kCaptureValue=1;
inline constexpr double kGoalValue=50;
inline constexpr double kWinValue=200;
inline constexpr double kCapturedValue=-1;
inline constexpr double kMaxUtil=kWinValue+scoreTarget*kGoalValue*2+(kMaxMoves/kNumPlayers-3)*kCaptureValue*2+(kMaxMoves/kNumPlayers/2-1)*kCaptureValue;


// State of a cell.
enum class CellState {
  kP0=0,
  kP1,
  kP2,
  kP3,
  kP4,
  kP5,
  kP6,
  kP7,
  kP8,
  kP9,
  kP10,
  kP11,
  kP12,
  kP13,
  kP14,
  kP15,
  kEmpty,
  kAGoal,
  kBGoal,
};

// State of an in-play game.
class FutlolState : public State {
 public:
  FutlolState(std::shared_ptr<const Game> game);

  FutlolState(const FutlolState&) = default;
  FutlolState& operator=(const FutlolState&) = default;

  Player CurrentPlayer() const override {
    return IsTerminal() ? kTerminalPlayerId : current_player_;
  }
  std::string ActionToString(Player player, Action action_id) const override;
  std::string ToString() const override;
  bool IsTerminal() const override;
  std::vector<double> Returns() const override { return returns_; }
  std::vector<double> Rewards() const override { return rewards_; }
  std::string InformationStateString(Player player) const override;
  std::string ObservationString(Player player) const override;
  void ObservationTensor(Player player,
                         absl::Span<float> values) const override;
  std::unique_ptr<State> Clone() const override;
  //void UndoAction(Player player, Action move) override;
  std::vector<Action> LegalActions() const override;
  CellState BoardAt(int cell) const { return board_[cell]; }
  CellState BoardAt(int row, int column) const {
    return board_[row * kNumCols + column];
  }

 protected:
  std::array<CellState, kNumCells> board_;
  void DoApplyAction(Action move) override;
  int oddTeamScore_ = 0;
  int evenTeamScore_ = 0;
  std::array<int, kNumPlayers> captures_ = {0};
  std::array<int, kNumPlayers> timesCaptured_ = {0};
  std::array<int, kNumPlayers> goals_ = {0};
  std::array<int, kNumPlayers> moves_ = {0};

 private:
  Player current_player_ = 0;         // Player zero goes first
  Player outcome_ = kInvalidPlayer;
  int num_turns_ = 0;
  std::vector<double> returns_ = std::vector<double>(kNumPlayers,0);
  std::vector<double> rewards_ = std::vector<double>(kNumPlayers,0);
};

// Game object.
class FutlolGame : public Game {
 public:
  explicit FutlolGame(const GameParameters& params);
  int NumDistinctActions() const override { return ((16+kNumCols)<<cellSize)+(int)CellState::kBGoal; }
  std::unique_ptr<State> NewInitialState() const override {
    return std::unique_ptr<State>(new FutlolState(shared_from_this()));
  }
  int NumPlayers() const override { return kNumPlayers; }
  double MinUtility() const override { return -1; }
  double UtilitySum() const override { return 0; }
  double MaxUtility() const override { return 1; }
  std::vector<int> ObservationTensorShape() const override {
    return {kCellStates, kNumRows, kNumCols};
  }
  int MaxGameLength() const override { return 1600; }
  std::array<double, kNumPlayers> self_weight_ = {0};
  std::array<double, kNumPlayers> team_weight_ = {0};
  bool oddWinOnly;
  bool evenWinOnly;
};

CellState PlayerToState(Player player);
std::string StateToString(CellState state);

inline std::ostream& operator<<(std::ostream& stream, const CellState& state) {
  return stream << StateToString(state);
}

}  // namespace futlol
}  // namespace open_spiel

#endif  // OPEN_SPIEL_GAMES_FUTLOL_H_
